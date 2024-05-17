import logging

from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_PLANT_STATE, ROUTING_KEY_LIDOPEN, ROUTING_KEY_ENERGY_SAVER_ENABLE, ROUTING_KEY_ENERGY_SAVER_STATUS
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.shared.protocol import ROUTING_KEY_UPDATE_CLOSED_CTRL_PARAMS


class EnergySaverServer:

    def __init__(self, error_threshold, ctrl_config_baseline, rabbit_config):
        self._l = logging.getLogger("EnergySaverServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(**rabbit_config)

        self.in_prediction_error = 0.0
        self.error_threshold = error_threshold

        self.ctrl_temperature_desired = ctrl_config_baseline['temperature_desired']

        # If false the anomaly will still be detected but energy saver is never actually turned on
        self.enable_energy_saver = True

    def setup(self):
        self.rabbitmq.connect_to_server()

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_ENERGY_SAVER_ENABLE, on_message_callback=self.change_energy_saver)

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_KF_PLANT_STATE,
                                on_message_callback=self.determine_lid_open)
        
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_LIDOPEN,
                                on_message_callback=self.change_desired_temperature)
    
    def start_monitoring(self):
        self.rabbitmq.start_consuming()

    def change_energy_saver(self, ch, method, properties, body_json):
        self._l.info(f"Changing enable_energy_saver to: {body_json}")
        self.enable_energy_saver = body_json["enable_energy_saver"]

    def determine_lid_open(self, ch, method, properties, body_json):
        self.in_prediction_error = body_json["fields"]["prediction_error"]
        is_open = abs(self.in_prediction_error) > self.error_threshold
        self._l.debug(f"Lid open: {is_open}")
        self.rabbitmq.send_message(ROUTING_KEY_LIDOPEN, {
            "lid_open": is_open,
        })

    def change_desired_temperature(self, ch, method, properties, body_json):
        if self.enable_energy_saver:
            lid_open = body_json["lid_open"]
            new_temp_desired = self.ctrl_temperature_desired*0.6 if lid_open else self.ctrl_temperature_desired
            self._l.debug(f"Desired temperature: {new_temp_desired} since lid_open is {lid_open}.")
            self.rabbitmq.send_message(ROUTING_KEY_ENERGY_SAVER_STATUS, {
                "energy_saver_on": lid_open,
            })
        else:
            new_temp_desired = self.ctrl_temperature_desired
            self._l.debug(f"Keeping desired temperature as enable_energy_saver = {self.enable_energy_saver}")
            self.rabbitmq.send_message(ROUTING_KEY_ENERGY_SAVER_STATUS, {
                "energy_saver_on": False,
            })
            
        self.rabbitmq.send_message(ROUTING_KEY_UPDATE_CLOSED_CTRL_PARAMS, {
            "temperature_desired": new_temp_desired,
        })