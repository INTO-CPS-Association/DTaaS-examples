#!/usr/bin/env python3
# license removed for brevity
#import rospy
#from std_msgs.msg import Int32

import pika
import json
from datetime import datetime
import time

#connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq-server-rabbitmq-1'))
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
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

    print(dt)

    msg = {}
    msg['time']= dt.isoformat()
    msg['someInt'] = 0

    for  i in range(1,100):
            msg['time']= datetime.now(tz = datetime.now().astimezone().tzinfo).isoformat(timespec='milliseconds')
            msg['someInt'] = i
            channel.basic_publish(exchange='fmi_digital_twin',
                          routing_key='data.to_cosim',
                          body=json.dumps(msg))
            print(" [x] Sent %s" % json.dumps(msg))
            msg['someInt'] = msg['someInt'] + 1
            time.sleep(0.1)

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
        pass
