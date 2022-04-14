#
#   Copyright 2021 Borja Nogales <bdorado@pa.uc3m.es>, Iván Vidal <ividal@it.uc3m.es>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from kafka import KafkaConsumer
from json import loads
import os
import threading
import time

# This function executes the Ansible playbook to configure a VNF
def ansible_controller(vnf_id, ip_address, username, password):

    try:
        #path = '/home/ividal/playbook_' + vnf_id + '.yaml'
        #call = ['ansible-playbook', path]
        #call = ['ansible-playbook', path]
        #subprocess.check_call(call)

        path = '/home/ividal/playbook.yaml'
        arguments = "-i " + ip_address + ", -e 'ansible_connection=ssh ansible_ssh_user=" + username + " ansible_ssh_pass=" + "{}".format(password) + " ansible_become_pass=" + "{}".format(password) + " ansible_python_interpreter=/usr/bin/python3'"


        os.system("ansible-playbook " + path + " " + arguments)

        with open('vnf_configuration.log', mode='a', encoding='utf-8') as log_file:
            log_file.write(str(time.time()) + ' Event: VNF ' + vnf_id + ' configured\n')

    except Exception:
        print('Exception: configuration of VNF', vnf_id, 'may have failed')

# Writes start time in the clof file
with open('vnf_configuration.log', mode='a', encoding='utf-8') as log_file:
    log_file.write(str(time.time()) + ' Event: consumer started\n')


#Initializes the kafka consumer
consumer = KafkaConsumer(
    'vnf.ready',
     bootstrap_servers=['10.4.48.25:9092'],
     value_deserializer=lambda x:
     loads(x.decode('utf-8'))
     )

# Defines a list of threads
threads = []

# Reads VNF registration events from the Kafka broker
for message in consumer:
    message = message.value
    vnf_id=message['vnf-id']
    ip_address=message['ip-address']
    username=message['username']
    password=message['password']

    now = time.time();

    print(now, ' -- Event: VNF', vnf_id, 'ready with IP Address', ip_address)

    with open('vnf_configuration.log', mode='a', encoding='utf-8') as log_file:
        log_file.write(str(now) + ' Event: VNF ' + vnf_id + ' ready with IP Address ' + ip_address + '\n')

    #Execute here the Ansible playbook in a thread,
    #using vnf_id (to locate the playbook name) and the IP address
    t = threading.Thread(target=ansible_controller, args=(vnf_id, ip_address, username, password))
    threads.append(t)
    t.start()
