#!/usr/bin/env python3
#

"""

Don't forget to install following modules and prepare virtual env:
$ virtualenv python3 venv
$ source venv/bin/activate
$ pip3 install dnslib weather

"""
import json
import socket
import argparse
import requests
from dnslib import DNSRecord, DNSHeader, RR, TXT, QTYPE, A, NS, textwrap, base64
from weather import Unit, Weather

# parsing arguments
__parser__ = argparse.ArgumentParser(description="weather through dns")
__parser__.add_argument('-s', '--host', default="0.0.0.0 53".split(),
                        dest='host', help='HOST PORT', nargs=2)
__parser__.add_argument('-f', '--zonefile', dest='zonefile', required=True)
__args__ = __parser__.parse_args()

# ip,port declaration
__ip__, __port__ = __args__.host

__sock__ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
__sock__.bind((__ip__, int(__port__)))

with open(__args__.zonefile, 'r') as zonefile:
    __zone__ = json.load(zonefile)

def parse_config(query_type=None):
    """Parsing zone config file"""
    domain = ''.join([i for i in __zone__])
    if query_type == 'A':
        var1 = __zone__[domain]['a']['ip']
        ttl = int(__zone__[domain]['a']['ttl'])
        return [var1, ttl]
    elif query_type == 'NS':
        var1 = __zone__[domain]['ns']['record']
        ttl = int(__zone__[domain]['ns']['ttl'])
        return [var1, ttl]
    else:
        return domain

def parse_request(data):
    """Parsing incomming data"""
    request = DNSRecord.parse(data)
    fqdn = [x.decode() for x in request.q.qname.label]
    city = '.'.join(fqdn[:-2])

    if '.'.join(fqdn[-2:]) == parse_config():
        # declare
        id_ = request.header.id
        rq_ = request.q
        qn_ = request.q.qname
        qt_ = request.q.qtype

        # generate message
        msg_ = get_weather(city)
        if msg_ is None:
            msg_ = "No city found, try: baku,moscow,nackhichevan"

        # generate dns reponse
        reply = DNSRecord(DNSHeader(id=id_, qr=1, aa=1, ra=1), q=rq_)
        if qt_ == QTYPE.A:
            if '.'.join(fqdn) == parse_config('A')[0]:
                ip_, ttl_ = parse_config('A')
                reply.add_answer(RR(qn_, qt_, rdata=A(ip_), ttl=ttl_))
            else:
                for ip_ in get_weather(city, 'A'):
                    reply.add_answer(RR(qn_, qt_, rdata=A('.'.join(ip_))))

        elif qt_ == QTYPE.TXT:
            if len(msg_) > 255:
                for msg in textwrap.wrap(msg_.decode(), 255):
                    reply.add_answer(RR(qn_, qt_, rdata=TXT(msg)))
            else:
                reply.add_answer(RR(qn_, qt_, rdata=TXT(msg_)))

        elif qt_ == QTYPE.NS:
            ns_, ttl_ = parse_config('NS')
            reply.add_answer(RR(qn_, qt_, rdata=NS(ns_), ttl=ttl_))
        return reply.pack()
    else:
        return None

def get_weather(city, record="TXT"):
    """Returing weather report"""
    if record == "A":
        wth = Weather(unit=Unit.CELSIUS).lookup_by_location(city)
        req = "{0}\n{1}\n{2} C\n{3} mph\n{4} mm".format(wth.title, wth.condition.text,
                                                        wth.condition.temp, wth.wind.speed,
                                                        wth.atmosphere['pressure'])
        lst = [str(ord(i)) for i in req]
        while len(lst) % 4 > 0:
            lst.append('32')
        itr = [iter(lst)]*4
        return zip(*itr)

    req = requests.get("http://wttr.in/{}?qp0".format(city)).content
    return base64.b64encode(req)
# run forever
while 1:
    __data__, __addr__ = __sock__.recvfrom(512)
    #parse_request(data)
    __sock__.sendto(parse_request(__data__), __addr__)
