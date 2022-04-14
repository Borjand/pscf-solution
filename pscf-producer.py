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

from time import sleep
from json import dumps
from kafka import KafkaProducer
import socket
import fcntl
import struct

# Gets the IP address assigned to ifname
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode('utf-8'))
    )[20:24])

# Initializes the Kafka producer
producer = KafkaProducer(bootstrap_servers=['10.4.48.25:9092'],
	value_serializer=lambda x:
    dumps(x).encode('utf-8')
    )

# Change ens3 by the interface name
ip_address = get_ip_address('ens3')

# Username of the VNF
username = 'ubuntu'

# Password for the user
password = 'ubuntu'

#Change "vnf-10" by the vnf identifier
vnf_id = 'vnf-12'

# Registers the data of the VNF in the Kafka broker
data = {'vnf-id' : vnf_id, 'ip-address' : ip_address, 'username' : username, 'password' : password}
producer.send('vnf.ready', value=data)
producer.flush()
