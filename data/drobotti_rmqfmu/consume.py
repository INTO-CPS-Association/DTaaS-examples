#!/usr/bin/env python3
import pika
from get_credentials import get_data
import sys


login_info = get_data()
if "username" in login_info:
    username = login_info["username"]
else: 
    print("Username should be provided in the credentials json file")
    sys.exit()
if "password" in login_info:
    password = login_info["password"]
else: 
    print("Password should be provided in the credentials json file")
    sys.exit()
if "hostname" in login_info:
    hostname = login_info["hostname"]
else: 
    print("Hostname should be provided in the credentials json file")
    sys.exit()
if "vhost" in login_info:
    vhost = login_info["vhost"]
else: 
    print("Vhost should be provided in the credentials json file")
    sys.exit()
if "port" in login_info:
    port = login_info["port"]
else: 
    print("port should be provided in the credentials json file")
    sys.exit()

#Create connection to rabbitMQ server
credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(hostname, port, vhost, credentials=credentials))

channel = connection.channel()

print("Declaring exchange")
channel.exchange_declare(exchange='fmi_digital_twin', exchange_type='direct')

print("Creating queue")
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='fmi_digital_twin', queue=queue_name,
                   routing_key='data.from_cosim')

print(' [*] Waiting for logs. To exit press CTRL+C')
print(' [*] I am consuming the commands sent from rbMQ')

def callback(ch, method, properties, body):
    print("Received [x] %r" % body)

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()

connection.close()
