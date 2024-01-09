#!/usr/bin/python3
import os
import sys
import time
import json
import random
from datetime import datetime
import uuid
import paho.mqtt.client as mqtt #import the client1
import config

broker_address = config.MQTT_SERVER
broker_port = config.MQTT_PORT

endLoop: int = 0

uesnr = '''f593e018-9c24-11ed-8ec3-00155d03fb30'''

def main() -> int:

  print('''UE Metric Topic''')
  uemep = mqtt.Client("uemetric_", uesnr) #create new instance
  uemep.username_pw_set(config.MQTT_USER, config.MQTT_PASS)
  uemep.connect(broker_address, broker_port, 60)  # connect to broker

  # nur einleifern, brauchen wir die loop ?
  uemep.loop_start()

  # endLoopmuss nicht syncronisiert werden.
  #  Es ist egal ob nun eine Metric mehroderweniger angeliefert wird
  iot_data = {  'measurements': {  'measurements': [  {  'channelIndex': 0
                                                       , 'timestamp':    0
                                                       , 'gasName':      "ch4"
                                                       , 'valueState':   "Valid"
                                                       , 'value':        { 'value': 2500, 'numDigits': 1, 'unit': "PPM"}
                                                       , 'alarmState':   { 'category': "CatNone", 'ackState': "NotAcknowledgable"}
                                                      }
                                                    , {  'channelIndex': 2
                                                       , 'timestamp':    0
                                                       , 'gasName':      "ch4"
                                                       , 'valueState':   "Valid"
                                                       , 'value':        { 'value': 1800, 'numDigits': 1, 'unit': "PPM"}
                                                       , 'alarmState':   { 'category': "CatNone", 'ackState': "NotAcknowledgable"}
                                                      }
                                                    , {  'channelIndex': 4
                                                       , 'timestamp':    0
                                                       , 'gasName':      "CO"
                                                       , 'valueState':   "Valid"
                                                       , 'value':        { 'value': 1800, 'numDigits': 1, 'unit': "PPM"}
                                                       , 'alarmState':   { 'category': "CatNone", 'ackState': "NotAcknowledgable"}
                                                      }
                                                   ]
                                 , 'dLightStatus': False
                                 , 'position': {  'latitude': 53.83867539593222
                                                , 'longitude': 10.660090262678677
                                                , 'elevation': 20
                                               }
                                 , 'device': "Direct_to_cloud_1"
                                }
              , 'device':  uesnr
             }
  while (endLoop == 0):
    # Der Gas Sensor bewegt sich
    iot_data['measurements']['position']['latitude']  = random.uniform(1, 58)
    iot_data['measurements']['position']['longitude'] = random.uniform(1, 9)
    iot_data['measurements']['position']['elevation'] = random.choice([-3, 0, 3, 6])
    for metric in iot_data['measurements']['measurements'] :
      metric['value']['value'] = metric['value']['value'] + (random.random()-0.5)
      metric['timestamp']      = int(datetime.now().strftime("%s"))

    # telegraf muss dan auf vgiot/ue/#/metric subscriben
    topic = config.MQTT_TOPIC_SENSOR + '/' + uesnr
    uemep.publish(topic, json.dumps(iot_data))
    print("Publishing to vgiot/ue/metric/" + uesnr)
    # print(json.dumps(iot_data))
    time.sleep(1)

  uemep.loop_stop()
  uemep.disconnect()


  return 0

if __name__ == '__main__':
  import sys
  sys.exit(main())
