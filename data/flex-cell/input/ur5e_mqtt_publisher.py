import paho.mqtt.client as mqtt
from threading import Timer
from pathlib import Path
import csv
import sched
import time
class UR5eMQTTPublisher():

    def __init__(self, filename,addr_mqtt="127.0.0.1",port_mqtt=1883,mqtt_topic="ur5e/actual/",mqtt_username="",mqtt_password="", frequency=50.0):
        self.addr_mqtt = addr_mqtt
        self.port_mqtt = port_mqtt
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.mqtt_topic = mqtt_topic
        self.filename = filename
        self.frequency = frequency
        self.mqtt_client = mqtt.Client()
        if (self.mqtt_username != ""):
            self.mqtt_client.username_pw_set(self.mqtt_username,password=self.mqtt_password)
        self.mqtt_client.connect(self.addr_mqtt,self.port_mqtt,60)
        mqtt_scheduler = sched.scheduler(time.time, time.sleep)
        mqtt_scheduler.enter(1/self.frequency, 1, self.publish_topics, (mqtt_scheduler,))
        mqtt_scheduler.daemon = True
        mqtt_scheduler.run()



    def publish_on_topic(self,topic,msg_data):
        #print("topic: ",topic, " - data: ",msg_data)
        self.mqtt_client.publish(self.mqtt_topic + topic,msg_data)

    def publish_topics(self,scheduler):
        try:
            scheduler.enter(1/self.frequency, 1, self.publish_topics, (scheduler,))
            topic_list = []
            with open(self.filename) as csv_file:
                csv_reader = csv.DictReader(csv_file,delimiter=" ")
                dict_from_csv = dict(list(csv_reader)[0])
                topic_list = list(dict_from_csv.keys())
            with open(self.filename) as csv_file:
                final_line = csv_file.readlines()[-1].split(" ")
            for i in range(len(topic_list)):
                self.publish_on_topic(topic_list[i],final_line[i])
        except:
            pass

'''if __name__ == '__main__':
    f_name = "ur5e_actual.csv"
    filename = Path("test_results") / Path(f_name)
    config_file =  Path("resources") / Path("record_configuration.xml")
    ur5e_mqtt_pub = UR5eMQTTPublisher(filename)
    ur5e_mqtt_pub.mqtt_client.loop_forever()'''
