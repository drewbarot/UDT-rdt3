'''
Dhrumil Barot
250970442
CS3357
Assn 3

This file is a UDP server.

'''

# Library Imports
import socket
import hashlib
import struct
import random
import time

'''
This part of the file defines some functions that we need to set up.
Functions:
    - Network_Delay():                                  Introduces Network Delay. Given. 
    - Network_Loss():                                   Introduces Network Loss. Given.  
    - Packet_Checksum_Corrupter(packetdata):            Corrupts checksums. Given.
    - create_checksum(packet):                          Create a checksum with the hashlib library. Function is prebuilt.  
    - formatServerData(ack_num, seq_num, data_bytes):   Format packet into a structure appropriate to send.
    - formatMessage(ack_num, seq_num, data_to_send):    Simple function to print the packet data. 
'''

# Define a function to introduce network delay. Function was provided in assignment. 
def Network_Delay():
    if False and random.choice([0,1,0]) == 1: # Set to False to disable Network Delay. Default is 33% packets are delayed
       time.sleep(.01)
       print("Packet Delayed")
    else:
        print("Packet Sent")

# Define a function to introduce network loss. Function was provided in assignment. 
def Network_Loss():
    if False and random.choice([0,1,1,0]) == 1: # Set to False to disable Network Loss. Default is 50% packets are lost
        print("Packet Lost")
        return(1)
    else:
        return(0)

# Define a function to corrupt the checksums. Function was provided in assignment. 
def Packet_Checksum_Corrupter(packetdata):
     if False and random.choice([0,1,0,1]) == 1:  # Set to False to disable Packet Corruption. Default is 50% packets are corrupt
        return(b'Corrupt!')
     else:
        return(packetdata)

# Define a function to create a checksum.
def create_checksum(packet):
	return bytes(hashlib.md5(packet).hexdigest(), encoding='UTF-8')

# Define a function to create a structure in the packet format.
def formatServerData(ack_num, seq_num, data_bytes):
    values = (ack_num, seq_num, data_bytes)
    data_packed = struct.Struct('I I 8s').pack(*values)
    checkSum = create_checksum(data_packed)
    data_values = (ack_num, seq_num, data_bytes, checkSum)
    return struct.Struct('I I 8s 32s').pack(*data_values)

# Define a function to format the packet to print.
def formatMessage(ack_num, seq_num, data_to_send):
    print("{ ack_num: ", ack_num, ", sequence_num: ", seq_num, ", data: " , data_to_send, " }")

'''
This part of the file is the main and executes the functons above. It also sets up some stuff. 
'''
print("Running UDP Server. ")
# Define the connection parameters. Use localhost and port 8080
IP_ADDRESS = "127.0.0.1"
PORT_NUMBER = 8080
RECEIVER_ADDRESS = (IP_ADDRESS, PORT_NUMBER)

# Create a socket. 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(RECEIVER_ADDRESS)
# The seq expected.
seq_num_expected = 0

# Perpetually run this loop.
while True:
    # Start by not slipping the seq. 
    flip_seq_num = False
    # Receive data and store the packet from recieved data. 
    data_received, client_address = sock.recvfrom(1024)
    packet = struct.Struct('I I 8s 32s').unpack(data_received)

    # Introduce a network delay.
    Network_Delay()
    # Introduce a potential network loss. 
    if Network_Loss():
        continue
    # Introduce a potential checksum correction. 
    data_modified = Packet_Checksum_Corrupter(packet[2])

    # Let user know that data was received. 
    print("Received the correct packet from the client: ", client_address)
    formatMessage(packet[0], packet[1], data_modified)
    # Some packet details.
    packet_packed = (packet[0], packet[1], data_modified)
    packet_final = struct.Struct('I I 8s').pack(*packet_packed)

    # Calculate the checksum. 
    checkSum_generated = create_checksum(packet_final)
    # Checksum verifications. 
    if checkSum_generated == packet[3] and seq_num_expected == packet[1]:
        # Data was not corrupt as checksum/seq are right. Set ack to 0, and store data.
        print("Packet received correctly. ")
        final_packet_data = formatServerData(0, packet[1], packet[2])
        # Flip the seq. 
        seq_num_expected = (seq_num_expected + 1) % 2
    elif checkSum_generated == packet[3]:
        # Data is corrupt as seq does not match. Set ack to 0, and store data. 
        print("Packet is corrupt. Checksum OK but seq is incorrect. ")
        final_packet_data = formatServerData(0, packet[1], packet[2])
    else:
        # Data is corrupt, checksum is wrong. Store data. 
        print("Packet is corrupt. Checksum is incorrect. ")
        flip_seq_num = True
        final_packet_data = formatServerData(0, (packet[1] + 1) % 2 , packet[2])
    
    # Send the packet from the server to the client. 
    sock.sendto(final_packet_data, client_address)
    print("Packet was sent to: ", client_address)
    formatMessage(0, (packet[1] + 1) % 2 if flip_seq_num == True else packet[1], packet[2])
    print()





