#!/usr/bin/python

# Python program that can send out M-SEARCH messages using SSDP (in server
# mode), or listen for SSDP messages (in client mode).

import sys
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

from twisted.web import server, resource
from twisted.internet.defer import succeed
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.web._newclient import ResponseFailed
from zope.interface import implements
import json
import time
import paramiko
from threading import Thread
import thread

#No idea where this came from but I left it
UUID = 'd1c58eb4-9220-11e4-96fa-123b93f75cba'
SEARCH_RESPONSE = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=30\r\nEXT:\r\nLOCATION:%s\r\nSERVER:Linux, UPnP/1.0, Lutron_Pi/1.0\r\nST:%s\r\nUSN:uuid:%s::%s'
SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900

MS = 'M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n' % (SSDP_ADDR, SSDP_PORT)

def determine_ip_for_host(host = None):
    """Determine local IP address used to communicate with a particular host"""
    
    if (host == None):
        print "it's null"
        host = '192.168.1.1'
    test_sock = DatagramProtocol()
    test_sock_listener = reactor.listenUDP(0, test_sock) # pylint: disable=no-member
    test_sock.transport.connect(host, 1900)
    my_ip = test_sock.transport.getHost().host
    test_sock_listener.stopListening()
    return my_ip
    
class StringProducer(object):
    """Writes an in-memory string to a Twisted request"""
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer): # pylint: disable=invalid-name
        """Start producing supplied string to the specified consumer"""
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self): # pylint: disable=invalid-name
        """Pause producing - no op"""
        pass

    def stopProducing(self): # pylint: disable=invalid-name
        """ Stop producing - no op"""
        pass
    
class Base(DatagramProtocol):

    def datagramReceived(self, data, (host, port)):
        first_line = data.rsplit('\r\n')[0]
        print "Received %s from %r" % (first_line, host, )

    def stop(self):
        pass
        
class StatusServer(resource.Resource):
    """HTTP server that handles requests from the SmartThings hub"""
    isLeaf = True
    def __init__(self, device_target, ssh):
        self.device_target = device_target
        self.ssh = ssh
        resource.Resource.__init__(self)
 
    def render_GET(self, request): # pylint: disable=invalid-name
        
        """Handle polling requests from ST hub"""
        if request.path == '/status':
            zone = request.content.read()
            if zone != "":
                print "specific device refresh"
                self.ssh.send('{"CommuniqueType":"ReadRequest","Header":{"Url":"/zone/%s/status"}}\n' % (zone))
                return
               
            '''Get status of all devices'''
            self.ssh.send('{"CommuniqueType":"ReadRequest","Header":{"Url":"/device"}}\n')
            response = self.ssh.channel.recv(9999)
            body = json.dumps(response)
            return response
            
        if request.path == '/on' or '/off' or '/setLevel':
        
            zoneLevel = request.content.read().split(':')
            self.ssh.send('{"CommuniqueType":"CreateRequest","Header":{"Url":"/zone/%s/commandprocessor"},"Body":{"Command":{"CommandType":"GoToLevel","Parameter":[{"Type":"Level","Value":%s}]}}}\n' % (zoneLevel[0], zoneLevel[1]))
            
#Client to respond to ssdp requests
class Client(Base):
    
    device_target = 'urn:schemas-upnp-org:device:RPi_Lutron_Caseta:%d' % (1)
    
    def __init__(self, iface):
        print "Running as client"
        self.iface = iface
        self.ssdp = reactor.listenMulticast(SSDP_PORT, self, listenMultiple=True)
        self.ssdp.setLoopbackMode(1)
        self.ssdp.joinGroup(SSDP_ADDR, interface=iface)

    def stop(self):
        self.ssdp.leaveGroup(SSDP_ADDR, interface=self.iface)
        self.ssdp.stopListening()
        
    def datagramReceived(self, data, (host, port)):
        try:
            header, _ = data.split('\r\n\r\n')[:2]
        except ValueError:
            return
        lines = header.split('\r\n')
        cmd = lines.pop(0).split(' ')
        lines = [x.replace(': ', ':', 1) for x in lines]
        lines = [x for x in lines if len(x) > 0]
        headers = [x.split(':', 1) for x in lines]
        headers = dict([(x[0].lower(), x[1]) for x in headers])

        search_target = ''
        if 'st' in headers:
            search_target = headers['st']
        
        if cmd[0] == 'M-SEARCH' and cmd[1] == '*' and search_target in self.device_target:
            url = 'http://%s:%d/status' % (determine_ip_for_host(host), 5000)
            response = SEARCH_RESPONSE % (url, search_target, UUID, self.device_target)
            self.ssdp.write(response, (host, port))
 
#Create the SSH connection to Smart Bridge
class smartBridgeSSH:
    shell = None
    client = None
    channel = None
    channel1 = None
    
    def __init__(self, host, uname, keyfilepath, smartThingsIP):
        self.host = host
        self.uname = uname
        self.smartThingsIP = smartThingsIP

        key = None
        port = 22
        keyfiletype = 'RSA'
        
        if keyfilepath is not None:
            key = paramiko.RSAKey.from_private_key_file(keyfilepath)
        
        # Create the SSH client.
        self.client = paramiko.SSHClient()
 
        # Setting the missing host key policy to AutoAddPolicy will silently add any missing host keys.
        # Using WarningPolicy, a warning message will be logged if the host key is not previously known
        # but all host keys will still be accepted.
        # Finally, RejectPolicy will reject all hosts which key is not previously known.
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the host.
        if key is not None:
            # Authenticate with a username and a private key located in a file.
            print "there is a key"
            self.client.connect(host, port, uname, None, key)
        else:
            # Authenticate with a username and a password.
            self.client.connect(host, port, uname, pwd)
        print self.client
        self.channel = self.openChannel()

        self.channel1 = self.openChannel()
        thread1 = Thread(target = self.listenOnChannel)
        thread1.start()
        
    def initalize(self):
        self.channel.send('{"CommuniqueType":"ReadRequest","Header":{"Url":"/device"}}\n')
        time.sleep(3)
        print self.channel.recv(9999)
        
        
    def openChannel(self):
        print self.client
        return self.client.invoke_shell()
        
    def listenOnChannel(self):
        while not self.channel.exit_status_ready():
            print "Listening"
            # Only print data if there is data to read in the channel
            output = self.channel.recv(9999)
            print output
            
            self.notifyDevices(output)
            
    def send(self, cmd):
        print "sending cmd" + cmd
        self.channel.send(cmd)
        
    def notifyDevices(self, output):
        
        body = json.dumps(output)
        host = 'http://' + self.smartThingsIP + ':39500'
        agent = Agent(reactor)
        req = agent.request(
            'POST',
            host,
            Headers({'Content-Type': ['application/json'], 'CONTENT-LENGTH': [str(len(output))]}),
            StringProducer(output)
            )

def main():
    
    #Please paste in the IP Address for your Lutron Smart Bridge and for your SmartThings Hub below!!
    smartBridgeIP = "192.168.1.22"
    smartThingsIP = "192.168.1.19"
    
    
    
    iface = determine_ip_for_host()
    device_target = 'urn:schemas-upnp-org:device:RPi_Lutron_Caseta:%d' % (1)
    obj = Client(iface)
    reactor.addSystemEventTrigger('before', 'shutdown', obj.stop)
    ssh = smartBridgeSSH(smartBridgeIP, "leap",'rsa_key', smartThingsIP) 
   
    # HTTP site to handle subscriptions/polling
    status_site = server.Site(StatusServer(device_target, ssh))
    reactor.listenTCP(5000, status_site) # pylint: disable=no-member
    
if __name__ == "__main__":
    reactor.callWhenRunning(main)
    reactor.run()
