import sys, os
incubator_location = os.getenv("INCUBATOR_PATH")
tessla_location = os.getenv("TESSLA_PATH")
lifecycle_location = os.getenv("LIFECYCLE_PATH")
sys.path.append(os.path.join(f"{incubator_location}"))
from incubator.config.config import load_config


def makeTelegrafConfig(template_path, dest_path):
    config = load_config(f"{incubator_location}/simulation.conf")
    try:
        with open(template_path, 'r') as file:
            content = file.read()

        content = content.replace('<AMQP_HOST>', config.get_string('rabbitmq.ip'))
        content = content.replace('<AMQP_PORT>', config.get_string('rabbitmq.port'))
        content = content.replace('<AMQP_VHOST>', config.get_string('rabbitmq.vhost'))
        content = content.replace('<AMQP_USER>', config.get_string('rabbitmq.username'))
        content = content.replace('<AMQP_PASS>', config.get_string('rabbitmq.password'))
        content = content.replace('<AMQP_EXCHANGE>', config.get_string('rabbitmq.exchange'))

        with open(dest_path, 'w') as file:
            file.write(content)

    except Exception as e:
        print(f"An error occurred while generating the telegraf config file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    makeTelegrafConfig(f"{lifecycle_location}/../telegraf.conf", f"{tessla_location}/telegraf.conf")
