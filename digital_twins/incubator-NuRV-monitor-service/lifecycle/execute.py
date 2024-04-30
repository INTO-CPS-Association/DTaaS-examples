import subprocess, os, time, sys, time
incubator_location = os.getenv("INCUBATOR_PATH")
sys.path.append(os.path.join(os.getcwd() + f"/{incubator_location}"))
sys.path.append(os.path.join(os.getcwd() + "/../../../common/services/NuRV"))
from threading import Thread, Event
from omniORB import CORBA
from omniORB.any import to_any
import Monitor
import CosNaming
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import load_config
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_ENERGY_SAVER_ENABLE, ROUTING_KEY_ENERGY_SAVER_STATUS, ROUTING_KEY_LIDOPEN


def startNuRV(ior):
    # overwrite relevant commands
    with open(os.getcwd() + "/../commands", "r+") as f:
        lines = f.readlines()
        lines[-1] = f"monitor_server -N {ior}"
        f.seek(0)
        f.writelines(lines)
        f.close()
    # Start NuRV monitor server    
    nurvPath = os.getenv("NURV_PATH")
    nurvProcess = subprocess.Popen(f"exec {nurvPath}/NuRV_orbit -source ../commands ../safe-operation.smv", shell=True, cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = nurvProcess.stdout.readline()
        if output == "" and nurvProcess.poll() is not None:
            print("Error starting NuRV server")
            break
        if "NuRV/Monitor/Service" in output:
            print("Started NuRV server")
            break

    orb = CORBA.ORB_init(["ORBInitRef", f"NameService={ior}"], CORBA.ORB_ID)
    obj = orb.resolve_initial_references("NameService")
    rootContext = obj._narrow(CosNaming.NamingContext)
    if rootContext is None:
        print("Failed to narrow the root naming context")
        sys.exit(1)

    # Resolve the name "NuRV/Monitor/Service"
    name = [CosNaming.NameComponent("NuRV", ""),
            CosNaming.NameComponent("Monitor", ""),
            CosNaming.NameComponent("Service", "")]
    try:
        obj = rootContext.resolve(name)

    except CosNaming.NamingContext.NotFound:
        print("Name not found")
        sys.exit(1)

    service = obj._narrow(Monitor.MonitorService)

    if service is None:
        print("Object reference is not an Monitor::Service")
        sys.exit(1)
    return nurvProcess, service


def startOmniNames():
    if not os.path.exists("../data"):
        os.system("mkdir ../data")
    cmd = "exec .venv/bin/omniNames -datadir ../data -start -always"
    omniNamesProcess = subprocess.Popen(cmd, shell=True, cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ior = ""
    while True:
        output = omniNamesProcess.stderr.readline()
        if output == '' and omniNamesProcess.poll() is not None:
            if ior == "":
                print("Error: Unable to find IOR reference")
                exit()
            break
        if "IOR:" in output:
            ior = "IOR:" + output.split("IOR:")[-1]
            print("Started omniNames server")
            break
    return omniNamesProcess, ior


def startRabbitMQ(message_callback):
    config = load_config(f"{incubator_location}/simulation.conf")
    rabbitMq = Rabbitmq(**config["rabbitmq"])
    rabbitMq.connect_to_server()
    print("Connected to rabbitmq server.")
    rabbitMq.subscribe(ROUTING_KEY_ENERGY_SAVER_STATUS, handleMessage)
    rabbitMq.subscribe(ROUTING_KEY_LIDOPEN, handleMessage)
    return rabbitMq


def startIncubator():
    print("Starting incubator")
    incubatorProcess = subprocess.Popen(f"cd {incubator_location}/; exec python -m startup.start_all_services", shell=True, cwd=os.getcwd(), stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    time.sleep(5)
    result = incubatorProcess.poll()
    if result is not None:
        print("Failed to start incubator")
        output = incubatorProcess.stderr.readlines()
        print(output)
        exit()
    return incubatorProcess

def verdictEnumToString(verdict):
    return f"{verdict}".split("_")[-1]

def runScenario(event, service):
    print("Running scenario with initial state: lid closed and energy saver on", flush=True)
    os.system(f"cd {incubator_location}; python -m cli.trigger_energy_saver")
    os.system(f"cd {incubator_location}; python -m cli.mess_with_lid_mock 1")
    for i in range(1200): # wait 2 minutes
        if event.is_set():
            return
        time.sleep(0.1)
    
    print("Opening lid...", flush=True)
    os.system(f"cd {incubator_location}; python -m cli.mess_with_lid_mock 100")
    for i in range(300): # wait 30 seconds
        if event.is_set():
            return
        time.sleep(0.1)
    
    print("Disabling energy saver...", flush=True)
    os.system(f"cd {incubator_location}; python -m cli.trigger_energy_saver --disable")
    for i in range(300):
        if event.is_set():
            return
        time.sleep(0.1)
    
    print("Putting lid back on...", flush=True)
    os.system((f"cd {incubator_location}; python -m cli.mess_with_lid_mock 1"))
    for i in range(300): # wait for the anomaly detection to determine that the lid is back on
        if event.is_set():
            return
        time.sleep(0.1)
        if i == 61:
            print("Resetting monitor...")
            service.reset(to_any(0), False)
    event.set()

def ensureNuRVRunning():
    # Start omniNames
    omniNamesProcess = None
    nurvProcess = None
    connectionEstablished = False
    while not connectionEstablished:
        try:
            omniNamesProcess, ior = startOmniNames()
            time.sleep(2)
            # Start NuRV
            nurvProcess, service = startNuRV(ior)
            time.sleep(10)
            result = service.heartbeat(to_any(0), "!anomaly & !energy_saving")
            if verdictEnumToString(result) == "Unknown":
                connectionEstablished = True
                print("Established connection with NuRV")
                service.reset(to_any(0), False)
                return omniNamesProcess, nurvProcess, service
        except:
            print("Failed to establish connection with NuRV. Retrying...")
            if nurvProcess is not None:
                nurvProcess.kill()
                nurvProcess.wait()
            if omniNamesProcess is not None:
                omniNamesProcess.kill()
                omniNamesProcess.wait()
            time.sleep(4)


if __name__ == "__main__":

    omniNamesProcess = None
    nurvProcess = None
    rabbitMq = None
    incubatorProcess = None
    scenario_thread = None
    try:
        omniNamesProcess, nurvProcess, service = ensureNuRVRunning()
        # Start incubator
        incubatorProcess = startIncubator()
        message = {}
        message["anomaly"] = "!anomaly"
        message["energy_saving"] = "!energy_saving"
        # setup RabbitMQ
        def handleMessage(channel, method, properties, body_json):
            result = ""
            if "lid_open" in body_json:
                message["anomaly"] = "anomaly" if body_json["lid_open"] else "!anomaly"
            elif "energy_saver_on" in body_json:
                message["energy_saving"] = "energy_saving" if body_json["energy_saver_on"] else "!energy_saving"
            states = f"{message['anomaly']} & {message['energy_saving']}"
            result = service.heartbeat(to_any(0), states)
            print(f"State: {states}, verdict: {verdictEnumToString(result)}")

            #if verdictEnumToString(result) == "True" or verdictEnumToString(result) == "False":
                #print("Resetting monitor...")
                #service.reset(to_any(0), False) # soft reset

            if event.is_set():
                rabbitMq.close()
        rabbitMq = startRabbitMQ(handleMessage)
        event = Event()
        scenario_thread = Thread(target=runScenario, args=(event,service))
        # Wait to ensure incubator running
        #time.sleep(1)
        scenario_thread.start()
        rabbitMq.start_consuming()
        print("Finished simulation")
    except KeyboardInterrupt:
        event.set()
        print("Stopping simulation...")
    except:
        event.set()
        print("An error has occurred")
    finally:
        if nurvProcess:
            print(f"Stopping nurvProcess with pid: {nurvProcess.pid}")
            nurvProcess.kill()
            nurvProcess.wait()
        if omniNamesProcess:
            print(f"Stopping omniNames with pid: {omniNamesProcess.pid}")
            omniNamesProcess.kill()
            omniNamesProcess.wait()
        if rabbitMq and not event.is_set():
            rabbitMq.close()
        if incubatorProcess:
            print(f"Stopping incubator with pid: {incubatorProcess.pid}")
            incubatorProcess.kill()
            incubatorProcess.wait()
        os.system("pkill -f \"python -m startup.start_all_services\"")
        if scenario_thread is not None:
            scenario_thread.join()
