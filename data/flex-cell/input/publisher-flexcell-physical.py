#!/usr/bin/env python3
from robots_flexcell import robots
import kukalbrinterface
import urinterface.robot_connection as urconn
import paho.mqtt.client as mqtt
import socket
import numpy as np
from pathlib import Path
import ur5e_mqtt_publisher

import pika
import json
from datetime import datetime
import time
from threading import Timer

from pyhocon import ConfigFactory
import logging

logging.disable(logging.CRITICAL)


ur_robot_model = robots.UR5e_RL()
kuka_robot_model = robots.KukaLBR_RL()
use_real_robots = False
mqtt_enabled = False

### pyhocon
conf = ConfigFactory.parse_file('/workspace/examples/data/flex-cell/input/connections.conf')
rabbitmq_host = conf.get_string('rabbitmq.hostname')
rabbitmq_port = conf.get_int('rabbitmq.port')
rabbitmq_username = conf.get_string('rabbitmq.username')
rabbitmq_password = conf.get_string('rabbitmq.password')
rabbitmq_vhost = conf.get_string('rabbitmq.vhost')

mqtt_host = conf.get_string('mqtt.hostname')
mqtt_port = conf.get_int('mqtt.port')
mqtt_username = conf.get_string('mqtt.username')
mqtt_password = conf.get_string('mqtt.password')

'''if use_real_robots:
    # Kuka
    kuka_f_name = "kukalbriiwa7_actual.csv"
    kuka_filename = "/workspace/examples/data/flex-cell/input/physical_twin/" + kuka_f_name
    kuka_robot = kukalbrinterface.RobotConnection("192.168.1.3",enabled_mqtt=mqtt_enabled,filename=kuka_filename)
    #kuka_robot.set_speed(0.01)
    # UR5e
    ur5e_ip = "192.168.1.2"
    ur5e_dashboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ur5e_controller_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ur5e_robot = urconn.RobotConnection(ur5e_ip,controller_socket=ur5e_controller_socket,dashboard_socket=ur5e_dashboard_socket) # Establish dashboard connection (port 29999) and controller connection (port 30002)
    f_name = "ur5e_actual.csv"
    filename = "/workspace/examples/data/flex-cell/input/physical_twin/" + f_name
    config_file =  "/workspace/examples/tools/flex-cell/resources/record_configuration.xml"
    ur5e_robot.start_recording(filename=filename, overwrite=True, frequency=50, config_file=config_file)
    if mqtt_enabled:
        ur5e_mqtt_pub = ur5e_mqtt_publisher.UR5eMQTTPublisher(filename,addr_mqtt=mqtt_host,port_mqtt=mqtt_port,mqtt_username=mqtt_username,mqtt_password=mqtt_password)
'''
#### Robots ####
def compute_ur_q(X,Y,Z):
    comp_x,comp_y,comp_z = ur_robot_model.compute_xyz_flexcell(X,Y,Z=Z)
    y_rot,z_rot = ur_robot_model.compute_yz_joint(comp_y,comp_z)
    target_position = ur_robot_model.compute_q(comp_x,y_rot,z_rot)[0]
    return target_position

def compute_kuka_q(X,Y,Z):
    comp_x,comp_y,comp_z = kuka_robot_model.compute_xyz_flexcell(X,Y,Z=Z)
    target_position = kuka_robot_model.compute_q(comp_x,comp_y,comp_z)[0]
    return target_position


def transmit_robot_motion(q,robot):
    if (robot == "UR5e"):
        if use_real_robots:
            ur5e_robot.movej(q=np.array(q))
        #for j in range(len(joint_pos)):
            #queue_server.send_string_ur(f"actual_q_{j} {joint_pos[j]}")
        #    pass
    elif (robot == "Kuka"):
        if use_real_robots:
            q_degrees = np.degrees(np.array(q))
            kuka_robot.move_ptp_rad(q=q_degrees)
        #for j in range(len(joint_pos)):
            #queue_server.send_string_kuka(f"actual_q_{j} {joint_pos[j]}")
        #    pass


#### RabbitMQ ####
credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, rabbitmq_vhost, credentials=credentials))
channel = connection.channel()
print("Declaring exchange")
channel.exchange_declare(exchange='fmi_digital_twin', exchange_type='direct')

print("Creating queue")
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='fmi_digital_twin', queue=queue_name,
                   routing_key='data.from_cosim')

#pub = rospy.Publisher('/Input', Int32, queue_size=10)
#rospy.init_node('talker', anonymous=True)
#rate = rospy.Rate(10) # 10hz
number = 1

def talker(number):
    consoleMsg = "About to publish %d" % number
    #rospy.loginfo(consoleMsg)
    #pub.publish(number)
    #rate.sleep()

def publish():
#    channel.stop_consuming()
    dt=datetime.strptime('2019-01-04T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")

    target_X_ur5e = 5
    target_Y_ur5e = 14
    target_Z_ur5e = 2
    target_X_kuka = 3
    target_Y_kuka = 10
    target_Z_kuka = 1

    msg = {}
    msg['time']= dt.isoformat()
    msg['target_X_ur5e'] = target_X_ur5e
    msg['target_Y_ur5e'] = target_Y_ur5e
    msg['target_Z_ur5e'] = target_Z_ur5e
    msg['target_X_kuka'] = target_X_kuka
    msg['target_Y_kuka'] = target_Y_kuka
    msg['target_Z_kuka'] = target_Z_kuka
    msg['command_move_ur5e'] = True
    msg['command_move_kuka'] = True
    msg['motion_time_ur5e'] = 1.0
    msg['motion_time_kuka'] = 1.0
    q_ur5e = compute_ur_q(target_X_ur5e,target_Y_ur5e,target_Z_ur5e)
    q_kuka = compute_kuka_q(target_X_kuka,target_Y_kuka,target_Z_kuka)
    #Timer(0.05, transmit_robot_motion, args=(q_ur5e,"UR5e",)).start()
    #Timer(0.05, transmit_robot_motion, args=(q_kuka,"Kuka",)).start()
    #transmit_robot_motion(q_ur5e,"UR5e")
    #transmit_robot_motion(q_kuka,"Kuka")

    for i in range(21):
            msg['time']= datetime.now(tz = datetime.now().astimezone().tzinfo).isoformat(timespec='milliseconds')
            print("i:" + str(i))

            if (i==9):
                target_X_ur5e = 4
                target_Y_ur5e = 18
                target_Z_ur5e = 1
                target_X_kuka = 4
                target_Y_kuka = 7
                target_Z_kuka = 2
                msg['target_X_ur5e'] = target_X_ur5e
                msg['target_Y_ur5e'] = target_Y_ur5e
                msg['target_Z_ur5e'] = target_Z_ur5e
                msg['target_X_kuka'] = target_X_kuka
                msg['target_Y_kuka'] = target_Y_kuka
                msg['target_Z_kuka'] = target_Z_kuka
                q_ur5e = compute_ur_q(target_X_ur5e,target_Y_ur5e,target_Z_ur5e)
                q_kuka = compute_kuka_q(target_X_kuka,target_Y_kuka,target_Z_kuka)
                #Timer(0.05, transmit_robot_motion, args=(q_ur5e,"UR5e",)).start()
                #Timer(0.05, transmit_robot_motion, args=(q_kuka,"Kuka",)).start()
                #transmit_robot_motion(q_ur5e,"UR5e")
                #transmit_robot_motion(q_kuka,"Kuka")

            if(i==35):
                target_X_ur5e = 0
                target_Y_ur5e = 20
                target_Z_ur5e = 3
                target_X_kuka = 6
                target_Y_kuka = 6
                target_Z_kuka = 3
                msg['target_X_ur5e'] = target_X_ur5e
                msg['target_Y_ur5e'] = target_Y_ur5e
                msg['target_Z_ur5e'] = target_Z_ur5e
                msg['target_X_kuka'] = target_X_kuka
                msg['target_Y_kuka'] = target_Y_kuka
                msg['target_Z_kuka'] = target_Z_kuka
                q_ur5e = compute_ur_q(target_X_ur5e,target_Y_ur5e,target_Z_ur5e)
                q_kuka = compute_kuka_q(target_X_kuka,target_Y_kuka,target_Z_kuka)
                Timer(0.05, transmit_robot_motion, args=(q_ur5e,"UR5e",)).start()
                Timer(0.05, transmit_robot_motion, args=(q_kuka,"Kuka",)).start()
                #transmit_robot_motion(q_ur5e,"UR5e")
                #transmit_robot_motion(q_kuka,"Kuka")

            ## Real robots

            channel.basic_publish(exchange='fmi_digital_twin',
                          routing_key='data.to_cosim',
                          body=json.dumps(msg))
            print(" [x] Sent %s" % json.dumps(msg))


            time.sleep(0.5)

def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    if "waiting for input data for simulation" in str(body):
      publish()
    else:
        print("Received: %s", str(body))
        number = 1
        talker(number)

if __name__ == '__main__':
    try:
        channel.basic_consume(
                    queue=queue_name, on_message_callback=callback, auto_ack=True)

        channel.start_consuming()

        connection.close()
    except KeyboardInterrupt:
        #ur5e_robot.stop_recording()
        pass
