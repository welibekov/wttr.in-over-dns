#!/usr/bin/env python3
#

"""

Don't forget to install following modules and prepare virtual env:
$ virtualenv python3 venv
$ source venv/bin/activate
$ pip3 install dnslib weather

"""
import sys
import json
import socket
import base64
import requests
from dnslib import DNSRecord,DNSHeader,RR,TXT,QTYPE,A,NS,textwrap
from weather import Unit,Weather

# ip,port declaration
ip = "127.0.0.1"
port = 15353

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((ip, port))

def parse_config(query_type=None):
    with open(sys.argv[1],'r') as zonefile:
        zone = json.load(zonefile)
        domain = ''.join([i for i in zone])
        if  query_type == 'A':
           a_domain = zone[domain]['a']['record']
           a_ip     = zone[domain]['a']['ip']
           a_ttl = int(zone[domain]['a']['ttl'])
           return [a_domain,a_ip,a_ttl]  
        elif query_type == 'NS':
            ns_domain = zone[domain]['ns']['record']
            ns_ttl = int(zone[domain]['ns']['ttl'])
            return [ns_domain,ns_ttl]
        else:
            return domain

def parse_request(data):
    request = DNSRecord.parse(data)
    fqdn = [x.decode() for x in (request.q.qname.label)]
    domain = '.'.join(fqdn[-2:])
    city = '.'.join(fqdn[:-2])
    if domain == parse_config():

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
            if '.'.join(fqdn) == parse_config('A')[0]:
                a,ip,ttl = parse_config('A')
                reply.add_answer(RR(QN,QT,rdata=A(ip),ttl=ttl))
            else:
                for ip in get_weather(city,'A'):
                    reply.add_answer(RR(QN,QT,rdata=A('.'.join(ip))))

        elif QT == QTYPE.TXT:
            if len(MSG) > 255:
                for msg in textwrap.wrap(MSG.decode(),255):
                    reply.add_answer(RR(QN,QT,rdata=TXT(msg)))
            else:
                reply.add_answer(RR(QN,QT,rdata=TXT(MSG)))

        elif QT == QTYPE.NS:
            ns,ttl = parse_config('NS')
            reply.add_answer(RR(QN,QT,rdata=NS(ns),ttl=ttl))
     
        return reply.pack()
    else:
        return None

def get_weather(city,record="TXT"):
    if record == "A":
        w=Weather(unit=Unit.CELSIUS).lookup_by_location(city)
        r="{0}\n{1}\n{2} C\n{3} mph\n{4} mm".format(w.title,w.condition.text,w.condition.temp,w.wind.speed,w.atmosphere['pressure'])
        l=[str(ord(i)) for i in r]
        while len(l)%4>0:
            l.append('32')
        it=[iter(l)]*4
        return zip(*it)

    r = requests.get("http://wttr.in/{}?qp0".format(city)).content
    return base64.b64encode(r)
    
    
# run forever
while 1:
    data, addr = sock.recvfrom(512)
    #parse_request(data)
    sock.sendto(parse_request(data), addr)
	
