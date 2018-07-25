#!/usr/bin/env python3
#

"""

Don't forget to install following modules and prepare virtual env:
$ virtualenv python3 venv
$ source venv/bin/activate
$ pip3 install dnslib weather

"""

import socket
import base64
import requests
import textwrap
from dnslib import DNSRecord,DNSHeader,RR,TXT,QTYPE,A,CNAME
from weather import Weather,Unit

# ip,port declaration
ip = "127.0.0.1"
port = 15353

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((ip, port))

def parse_request(data):
    request = DNSRecord.parse(data)
    fqdn = [x.decode() for x in (request.q.qname.label)]
    domain = '.'.join(fqdn[-2:])
    city = '.'.join(fqdn[:-2])
    if wttr_in(domain):

        # declare
        ID=request.header.id
        RQ=request.q
        QN=request.q.qname
        QT=request.q.qtype

        # generate message
        MSG=get_weather(city)
        if MSG is None:
            MSG="No city found, try: baku,moscow,nackhichevan"
		
        # generate dns reponse
        reply=DNSRecord(DNSHeader(id=ID,qr=1,aa=1,ra=1),q=RQ)
    
        if QT == QTYPE.A:
            reply.add_answer(RR(QN,QT,rdata=A("{}.{}.1.1".format(25,50))))

        elif QT == QTYPE.TXT:
            if len(MSG) > 255:
                for msg in textwrap.wrap(MSG.decode(),255):
                    reply.add_answer(RR(QN,QT,rdata=TXT(msg)))
            else:
                reply.add_answer(RR(QN,QT,rdata=TXT(MSG)))

    return reply.pack()

# check 
def wttr_in(domain):
    return domain == 'wttr.in'

def get_weather(city):
    
    """
    weather = Weather(unit=Unit.CELSIUS)
    l = weather.lookup_by_location(city)
    if l is None:
        return None
    else:
        weather_report = "City:{}\nTemp:{}\nGeneral:{}\nHumiditi:{}\n".format(city,l.condition.temp,
									    l.condition.text,
									    l.atmosphere['humidity'])
    
    return base64.b64encode(weather_report.encode())
    """
    r = requests.get("http://wttr.in/{}?qp0".format(city)).content
    return base64.b64encode(r)
    
# run forever
while 1:
    data, addr = sock.recvfrom(512)
    sock.sendto(parse_request(data), addr)
	
