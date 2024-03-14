import concurrent.futures
import logging
import time

# Import parameters and shared stuff
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.shared.protocol import *
from incubator.config.config import config_logger, load_config

CTRL_EXEC_INTERVAL = 3.0


class IncubatorDriver:

    def __init__(self,
                 heater,
                 fan,
                 t1,
                 t2,
                 t3,
                 rabbit_config,
                 simulate_actuation=True
                 ):

        self.logger = logging.getLogger("IncubatorDriver")
        # Connection info
        self.rabbitmq = Rabbitmq(**rabbit_config)

        self.heater_queue_name = ""
        self.fan_queue_name = ""

        # IO
        self.heater = heater
        self.fan = fan
        self.temperature_sensor = (t1, t2, t3)

        # Safety
        self.simulate_actuation = simulate_actuation

        # Always start in safe mode.
        self.actuators_off()

    def setup(self):
        self.rabbitmq.connect_to_server()
        self.logger.info("Connected.")
        self.fan_queue_name = self.rabbitmq.declare_local_queue(routing_key=ROUTING_KEY_FAN)
        self.heater_queue_name = self.rabbitmq.declare_local_queue(routing_key=ROUTING_KEY_HEATER)

    def cleanup(self):
        self.logger.debug("Cleaning up.")
        self.actuators_off()
        self.rabbitmq.close()

    def actuators_off(self):
        self.fan.off()
        self.heater.off()

    def control_loop(self, exec_interval=CTRL_EXEC_INTERVAL, strict_interval=True):
        try:
            while True:
                start = time.time()
                self.control_step(start, exec_interval)
                elapsed = time.time() - start
                if elapsed > exec_interval:
                    self.logger.error(
                        f"Control step taking {elapsed - exec_interval}s more than specified interval {exec_interval}s. Please specify higher interval.")
                    if strict_interval:
                        raise ValueError(exec_interval)
                else:
                    print(f"Sleeping for {exec_interval - elapsed}")
                    time.sleep(exec_interval - elapsed)
        except:
            self.cleanup()
            raise

    def control_step(self, start, exec_interval):
        self.react_control_signals(start)
        self.read_upload_state(start, exec_interval)

    def react_control_signals(self, start):
        heat_cmd = self._try_read_heat_control()
        self.logger.debug(f"Elapsed after get heat command: {time.time() - start}s")
        fan_cmd = self._try_read_fan_control()
        self.logger.debug(f"Elapsed after get fan command: {time.time() - start}s")

        if heat_cmd is not None:
            self.logger.debug(f"Heat command: on={heat_cmd}")
            self._safe_set_actuator(self.heater, heat_cmd)
            self.logger.debug(f"Elapsed after set heater: {time.time() - start}s")
        if fan_cmd is not None:
            self.logger.debug(f"Fan command: on={fan_cmd}")
            self._safe_set_actuator(self.fan, fan_cmd)
            self.logger.debug(f"Elapsed after set fan: {time.time() - start}s")

    def _safe_set_actuator(self, gpio_led, on: bool):
        if on and gpio_led.is_lit:
            self.logger.debug(f"  Ignored command as it is already on.")
            return
        elif (not on) and (not gpio_led.is_lit):
            self.logger.debug(f"  Ignored command as it is already off.")
            return

        if on:
            if not self.simulate_actuation:
                gpio_led.on()
            else:
                self.logger.info("Pretending to set actuator on.")
        else:
            if not self.simulate_actuation:
                gpio_led.off()
            else:
                self.logger.info("Pretending to set actuator off.")

    def read_upload_state(self, start, exec_interval):
        n_sensors = len(self.temperature_sensor)
        readings = [None] * n_sensors
        timestamps = [None] * n_sensors

        assert len(readings) == n_sensors
        assert len(timestamps) == n_sensors

        # Use concurrency to read temp sensors in parallel.
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_sensors) as executor:
            tasks = {executor.submit(self.temperature_sensor[i].read): i for i in range(n_sensors)}
            for task in concurrent.futures.as_completed(tasks):
                i = tasks[task]
                try:
                    data = task.result()
                    readings[i] = float(data)
                    self.logger.debug(f"Elapsed after read sensor {i}: {time.time() - start}s")
                    timestamps[i] = time.time_ns()
                except Exception as exc:
                    self.logger.error(f"Problem reading sensor {i}: {exc}")
                    raise exc

        assert all([v is not None for v in readings])
        assert all([ts is not None for ts in timestamps])

        timestamp = time.time_ns()
        message = {
            "measurement": "low_level_driver",
            "time": timestamp,
            "tags": {
                "source": "low_level_driver"
            },
            "fields": {
                "t1": readings[0],
                "time_t1": timestamps[0],
                "t2": readings[1],
                "time_t2": timestamps[1],
                "t3": readings[2],
                "time_t3": timestamps[2],
                "average_temperature": (readings[0] + readings[1]) / 2,
                "heater_on": self.heater.is_lit,
                "fan_on": self.fan.is_lit,
                "execution_interval": exec_interval,
                "elapsed": time.time() - start
            }
        }

        self.rabbitmq.send_message(ROUTING_KEY_STATE, message)
        self.logger.debug(f"Message sent to {ROUTING_KEY_STATE}.")
        self.logger.debug(message)
        self.logger.debug(f"Elapsed after msg sent: {time.time() - start}s")

    def _try_read_heat_control(self):
        msg = self.rabbitmq.get_message(self.heater_queue_name)
        if msg is not None:
            return msg["heater"]
        else:
            return None

    def _try_read_fan_control(self):
        msg = self.rabbitmq.get_message(self.fan_queue_name)
        if msg is not None:
            return msg["fan"]
        else:
            return None


if __name__ == '__main__':
    from incubator.physical_twin.sensor_actuator_layer import Heater, Fan, TemperatureSensor

    config_logger("logging.conf")
    l = logging.getLogger("low_level_driver_server")
    config = load_config("simulation.conf")

    incubator = IncubatorDriver(heater=Heater(12),
                                fan=Fan(13),
                                t1=TemperatureSensor("/sys/bus/w1/devices/10-0008039ad4ee/w1_slave"),
                                t2=TemperatureSensor("/sys/bus/w1/devices/10-0008039b25c1/w1_slave"),
                                t3=TemperatureSensor("/sys/bus/w1/devices/10-0008039a977a/w1_slave"),
                                rabbit_config=config["rabbitmq"],
                                simulate_actuation=False)
    while True:
        try:
            incubator.setup()
            incubator.control_loop(strict_interval=False)
        except KeyboardInterrupt:
            exit(0)
        except Exception as exc:
            l.error("The following exception occurred. Attempting to reconnect.")
            l.error(exc)
            time.sleep(1.0)
