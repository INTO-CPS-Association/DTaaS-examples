from pyhocon import ConfigFactory
from pyhocon import HOCONConverter
import xml.etree.ElementTree as ET


conf = ConfigFactory.parse_file('/workspace/examples/data/flex-cell/connections.conf')
rabbitmq_host = conf.get_string('rabbitmq.hostname')
rabbitmq_port = conf.get_int('rabbitmq.port')
rabbitmq_username = conf.get_string('rabbitmq.username')
rabbitmq_password = conf.get_string('rabbitmq.password')

mqtt_host = conf.get_string('mqtt.hostname')
mqtt_port = conf.get_int('mqtt.port')
mqtt_username = conf.get_string('mqtt.username')
mqtt_password = conf.get_string('mqtt.password')

## Config files
kuka_conf = ConfigFactory.parse_file('/workspace/examples/digital_twins/flex-cell/kuka_actual.conf')
ur5e_conf = ConfigFactory.parse_file('/workspace/examples/digital_twins/flex-cell/ur5e_actual.conf')

kuka_conf.pop("mqtt.ip")
kuka_conf.put("mqtt.ip",mqtt_host)
kuka_conf.pop("mqtt.port")
kuka_conf.put("mqtt.port",mqtt_port)
kuka_conf.pop("mqtt.username")
kuka_conf.put("mqtt.username",mqtt_username)
kuka_conf.pop("mqtt.password")
kuka_conf.put("mqtt.password",mqtt_password)
HOCONConverter().to_hocon(kuka_conf)
with open('/workspace/examples/digital_twins/flex-cell/kuka_actual.conf', 'w') as f:
    print(HOCONConverter().to_hocon(kuka_conf), file=f)
    f.close()


ur5e_conf.pop("mqtt.ip")
ur5e_conf.put("mqtt.ip",mqtt_host)
ur5e_conf.pop("mqtt.port")
ur5e_conf.put("mqtt.port",mqtt_port)
ur5e_conf.pop("mqtt.username")
ur5e_conf.put("mqtt.username",mqtt_username)
ur5e_conf.pop("mqtt.password")
ur5e_conf.put("mqtt.password",mqtt_password)
with open('/workspace/examples/digital_twins/flex-cell/ur5e_actual.conf', 'w') as f:
    print(HOCONConverter().to_hocon(ur5e_conf), file=f)
    f.close()

## modelDescription file
md_file = ET.parse('/workspace/examples/models/flex-cell/modelDescription.xml')
root = md_file.getroot()
model_vars = root.find("ModelVariables")
for variable in model_vars:
    if variable.attrib["name"] == "config.hostname":
        hostname_xml = variable.find("String")
        hostname_xml.attrib["start"] = rabbitmq_host
    elif variable.attrib["name"] == "config.port":
        port_xml = variable.find("Integer")
        port_xml.attrib["start"] = str(rabbitmq_port)
    elif variable.attrib["name"] == "config.username":
        username_xml = variable.find("String")
        username_xml.attrib["start"] = rabbitmq_username
    elif variable.attrib["name"] == "config.password":
        password_xml = variable.find("String")
        password_xml.attrib["start"] = rabbitmq_password

md_file.write('/workspace/examples/models/flex-cell/modelDescription.xml')