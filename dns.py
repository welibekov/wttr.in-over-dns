#!/usr/bin/python3
#
# int('11111111',2) -> convert to integer, 2 means 'binary'
# format(123,'b') -> convert to binary
# ' '.join(format(ord(x), 'b') for x in sting) -> return binary
# ' '.join(format(x, 'b') for x in bytarray(string))
# binary '&' operator can give us exactly byte in position
# binary '<<' shift byte operation, can return square of 2 if base 1:
# 1<<1 == 2; 1<<2 == 4; 1<<3 == 8; 1<<4 == 16; etc.
#

import socket

port = 15353
ip = "127.0.0.1"


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))


def getflags(flags):
    
    byte1 = bytes(flags[:1])
    byte2 = bytes(flags[1:2])

    rflags = ''

    QR = '1'
    
    OPCODE = ''
    for bit in range(1,5):
        OPCODE += str(ord(byte1)&(1<<bit))

    AA = '1'
    
    TC = '0'

    RD = '0'
    
    RA = '0'

    Z = '000'
    
    RCODE = '0000'

    return int(QR+OPCODE+AA+TC+RD, 2).to_bytes(1, byteorder='big')+int(RA+Z+RCODE, 2).to_bytes(1, byteorder='big')

def getquestiondomain(data):

    state = 0
    expectedlenght = 0
    domainstring = ''
     
    for byte in data:
        if state == 1:
            domainstring = chr(byte)    
        else:
            state = 1
            expectedlenght = byte
        
        print(domainstring)
    
def buildresponse(data):
    
    # Transaction ID
    TransactionID = data[:2]
    TID = ''
    for byte in TransactionID:
        TID += hex(byte)[2:]

    # Get the flags
    Flags = getflags(data[2:4])

    # Question Count
    QDCOUNT = b'\x00\x01'

    # Address Count
    getquestiondomain(data[12:])

while 1:
    data, addr = sock.recvfrom(512)
    r = buildresponse(data)
    sock.sendto(r, addr)
    


