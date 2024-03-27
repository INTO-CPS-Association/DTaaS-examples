import logging
from datetime import datetime

import pytz

from cli.run_plant_simulation import run_plant_simulation
from incubator.config.config import load_config
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_PLANTCALIBRATOR4
from incubator.communication.server.rpc_client import RPCClient
from incubator.communication.shared.protocol import from_s_to_ns
from incubator.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from startup.utils.logging_config import config_logging

if __name__ == '__main__':
    params = four_param_model_params

    C_air = params[0]
    G_box = params[1] + 2.0
    C_heater = params[2]
    G_heater = params[3]
    initial_heat_temperature = 24.0

    start_date = datetime.fromisoformat("2021-01-10 10:24:00").astimezone(pytz.utc)
    end_date = datetime.fromisoformat("2021-01-10 10:31:00").astimezone(pytz.utc)
    print(f"start_date={start_date}")
    print(f"end_date={end_date}")

    end_date_ns = from_s_to_ns(end_date.timestamp())
    start_date_ns = from_s_to_ns(start_date.timestamp())

    config_logging(level=logging.WARN)
    config = load_config("simulation.conf")
    client = RPCClient(**(config["rabbitmq"]))
    client.connect_to_server()

    reply = client.invoke_method(ROUTING_KEY_PLANTCALIBRATOR4, "run_calibration",
                                 {
                                     "calibration_id": "2021-01-10 10:24:00",
                                     "start_date_ns": start_date_ns,
                                     "end_date_ns": end_date_ns,
                                     "Nevals": 100,
                                     "commit": False,
                                     "record_progress": True,
                                     "initial_heat_temperature": initial_heat_temperature,
                                     "initial_guess": {
                                         "C_air": C_air,
                                         "G_box": G_box,
                                         "C_heater": C_heater,
                                         "G_heater": G_heater
                                     }
                                 })
    params = [reply["C_air"],
              reply["G_box"],
              reply["C_heater"],
              reply["G_heater"]]
    print(reply)
    run_plant_simulation(params, start_date, end_date, initial_heat_temperature, record=False)
