#!/usr/bin/env python3
import pika
import json
import datetime
import time
import ssl

credentials = pika.PlainCredentials('mirgita', 'MirgitaUsesDTaaS')
connection = pika.BlockingConnection(pika.ConnectionParameters('dtl-server-2.st.lab.au.dk', 8089, credentials=credentials))

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
