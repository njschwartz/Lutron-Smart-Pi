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
import telnetlib
from threading import Thread
import thread
import StringIO

#from zeroconf import ServiceBrowser, Zeroconf
import ipaddress

#No idea where this came from but I left it
UUID = 'd1c58eb4-9220-11e4-96fa-123b93f75cba'
SEARCH_RESPONSE = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=30\r\nEXT:\r\nLOCATION:%s\r\nSERVER:Linux, UPnP/1.0, Lutron_Pi/1.0\r\nST:%s\r\nUSN:uuid:%s::%s'
SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900
SMARTTHINGS_IP = "YOUR IP HERE"
SMARTBRIDGE_IP = "YOUR IP HERE"
PRO_BRIDGE = False
MS = 'M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n' % (SSDP_ADDR, SSDP_PORT)

my_key = """\
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEApX6g2uGLyC8ZDw13Vvn/lgp4pf5BrEy2oZf+yFouGOn+UI+J
7d9yWWrP8nUJXIzz1YQ3Fs4YgDFus5bu1g/3XuK3J7kk5lVuz3wTgqDGw2jIP3mb
IUIlonEvJp+5aKNjMUkFGHkWo6nlqXx0nQjFrqhU1bZTPKwKON35IrauqmQaI+z7
pA2DEW1w2a/sO+Y4t/iBzTU0U4M9C/5PcT5GRtfb23RFP5NaiE38OC68rWfqFR91
+37smywvX1vaxhVbP5DkZXtZNBDK5jXtQ3j0dHwnKSyu7JDmhhq/pHgMEZaxtAjE
ziFJdP56P8Hy0TdXcvG/Wfw+F94KltOsp/wJfQIDAQABAoIBABvlX2nl0PEad0fh
RjeEBoAdHb8lP56yg6pze3/8K38JmlOsDlzpaFYIOistbTmLjOJ12e9fKCQbsQRW
scWlhVYaMzNf8wdcaURSLtu7DCYOOIryjaKqirt6Bq+lBtTLjcHWBCTe7GEEF3Fd
SC7cNq49M6eehyNYAJUbXY5rar/PwEpKFE/5LuTP4xXjJCvCsMffcenBj/rZp7g8
nigZ4pboNJNY7ODpTg4J2tk6x5HPSoYr9aM8CL4IjG4pcoJe8ROXm5YM+JQSwL1d
nUH4SA4qQOpE3cHLtxfmAoJ8vwu7tIpxD5YMMAACg1dVZGPgVVSOlTXH9jxC2vfn
GVQa98ECgYEA27HMMeWPFbgVuscR6cVmCriAuKlhYvJJkhYFjJV8qWMvgwsjOdl6
O1wGzW4IWSzzSoz0MdBs1ikUj1FlfriGpRWBQkT7rdIGwbKus3BXSIt52b/3cCvx
2H1qS/P9gAW8yfw6LcIGA9L26BOWCDqtmMX1aJ/zkVdrafr7AOIf+w0CgYEAwNfm
AW3oSald1NpG1CoB6rA7VJg9ulXm2t0Ha8czQ483pFjkDaaETQyIO+dtTg1sqrbO
dcFn+FF66fBlQN/ZNGb9+IbGSdITkI5iV5D1RSXJVuxaZFkX6IZPwwBgL6ouBPW2
lNfg06j4RKj32fddPxtjJIwTkOo6VUbSCbbh7DECgYBjDuIRRX6kvmId25C6JWWD
Q/nWSZk9sh12HzPVVbnl7nEH10fE18iDZ1Ux34EoJFp2rOOWanIIhnFcxcjLwIwF
d5LWvJ/2mhKt19Fp2yef8DO6+RGqpEXh5Xq+UH9m8C9Vq8LXyvpHUyI9NkeZ4ktP
7UJgMG70g8RM/vuaRFtDKQKBgGHD0qZ82tulUp2bf3cGSOx7JckQWZMDA8OHdMCu
P44LqHDYY92Lwtzw8ow0GpUMdz/g57CJObWJUWAScLLACXTole8OHK7GIwcROEge
hEnnCzjXIEhpZpaKqRs6MIlZpHT9QPAata94pUzhwK2vG4Xn045uuWipZqNfARLN
taGxAoGAQGFYb63lBeGS2vkUyovP2kMwBF0E6Y+3Il+TGjwPalyg+TyNzEAvkOUe
2iy8Eul9rT6qcByzNXnNAMRHYhXDWQWmRaHM/lzyIkNr/O3UBEQKiSew/YhH6s1W
iMwh+x+ekyFOxb98aNqlnEH/7PsQonzWThpzcAAojllTt9AIbbc=
-----END RSA PRIVATE KEY-----"""
    
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
                self.ssh.send('{"CommuniqueType":"ReadRequest","Header":{"Url":"/zone/%s/status"}}\n' % (zone))
                return
                
            request.responseHeaders.addRawHeader(b"content-type", b"application/json")    
            return self.getAllSwitches();

        elif request.path == '/on' or request.path == '/off' or request.path == '/setLevel':
            zoneLevel = request.content.read().split(':')
            self.ssh.send('{"CommuniqueType":"CreateRequest","Header":{"Url":"/zone/%s/commandprocessor"},"Body":{"Command":{"CommandType":"GoToLevel","Parameter":[{"Type":"Level","Value":%s}]}}}\n' % (zoneLevel[0], zoneLevel[1]))
    
        elif request.path == '/switches':
            request.responseHeaders.addRawHeader(b"content-type", b"application/json")    
            return self.getAllSwitches();
            
        elif request.path == '/scenes':
            request.responseHeaders.addRawHeader(b"content-type", b"application/json")    
            return self.getAllScenes()
        
        elif request.path == '/scene':
            scene = request.content.read()
            if scene != "":
                self.ssh.send('{"CommuniqueType": "CreateRequest","Header": {"Url": "/virtualbutton/%s/commandprocessor"},"Body": {"Command": {"CommandType": "PressAndRelease"}}}\n' % (scene))
                return

    def getAllSwitches(self):
        '''Get status of all devices'''
        self.ssh.channel1.send('{"CommuniqueType":"ReadRequest","Header":{"Url":"/device"}}\n')
        response = self.ssh.channel1.recv(99999)
        splitResponse = response.splitlines()
        if len(splitResponse) == 1:
            response = splitResponse[0]
        else:
            response = splitResponse[1]
            
        try:
            body = json.dumps(json.JSONDecoder().decode(response)) 
            if (body.find("PRO") != -1):
                print "Pro Bridge Found"
                proBridgeSetup()
                return body
            elif (body.find("BDG") != -1):
                print "Standard Bridge Found"
                return body
        except ValueError: 
            print "Not valid JSON~This error may be normal the first time so don't stress!"
        
    def getAllScenes(self):

        self.ssh.channel1.send('{"CommuniqueType":"ReadRequest","Header":{"Url":"/virtualbutton"}}\n')

        response = self.ssh.channel1.recv(99999)
        splitResponse = response.splitlines()
        if len(splitResponse) == 1:
            response = splitResponse[0]
        else:
            response = splitResponse[1]
            
        body = json.dumps(json.JSONDecoder().decode(response)) 
        return body

    def getAllPicos(self):
        return
        
        
    
            
#Client to respond to ssdp requests
class Client(Base):
    
    device_target = 'urn:schemas-upnp-org:device:RPi_Lutron_Caseta:%d' % (1)
    
    def __init__(self, iface):
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
            print "Your SmartThings Hub IP Address is: " + host
            url = 'http://%s:%d/status' % (determine_ip_for_host(host), 5000)
            response = SEARCH_RESPONSE % (url, search_target, UUID, self.device_target)
            self.ssdp.write(response, (host, port))
    
class smartBridgeTELNET:
    #session = None
    
    def __init__(self, bridgeIP):
        self.bridgeIP = bridgeIP
        self.session = self.login();
         
         
    def login(self):
        connection = False
        self.session = telnetlib.Telnet(self.bridgeIP, 23)
        while connection is False:
            print 'Attempting to connect to Lutron Hub'
            self.session.read_until("login:")
            self.session.write('lutron\r\n')
            self.session.read_until("password")
            self.session.write('integration\r\n')
            prompt = self.session.read_until('GNET')
            connection = True
        print "Successfully Logged in to Lutron Hub"
        thread3 = Thread(target = self.listenForData)
        thread3.start()
        return self.session
    
    def listenForData(self):
        print "Listening for Telnet DATA"
        while (self.session) :
            response = self.session.read_some().split(",")
            if response[0].startswith("~") :
                for value in response:
                    print value
                #[Body:[ZoneStatus:[Level:100, Zone:[href:/zone/5]]], Header:[StatusCode:200 OK, MessageBodyType:OneZoneStatus, Url:/zone/5/status/level], CommuniqueType:ReadResponse]  
                #'{"CommuniqueType": "CreateRequest","Header": {"Url": "/virtualbutton/%s/commandprocessor"},"Body": {"Command": {"CommandType": "PressAndRelease"}}}\n' % (scene))
                output = {
                    "Body" : {"Device" : response[1], "Button" : response[2], "Action" : response[3]},
                }
                notifyDevices(json.dumps(output))

#Create the SSH connection to Smart Bridge
class smartBridgeSSH:
    
    #def __init__(self, host, uname, keyfilepath, smartThingsIP):
    def __init__(self):
        #self.host = host
        uname = 'leap'
        key = None
        port = 22
        keyfiletype = 'RSA'

        '''
        if keyfilepath is not None:
            key = paramiko.RSAKey.from_private_key_file(keyfilepath)
        '''
        
        key = paramiko.RSAKey.from_private_key(StringIO.StringIO(my_key))
        # Create the SSH client.
        self.client = paramiko.SSHClient()
 
        # Setting the missing host key policy to AutoAddPolicy will silently add any missing host keys.
        # Using WarningPolicy, a warning message will be logged if the host key is not previously known
        # but all host keys will still be accepted.
        # Finally, RejectPolicy will reject all hosts which key is not previously known.
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
          
        # Connect to the host.
        if key is not None:
            # Authenticate with a username and a private key
            self.client.connect(SMARTBRIDGE_IP, port, uname, None, key)
        
        #Open a listening channel and a sending channel
        self.channel = self.openChannel()
        self.channel1 = self.openChannel()
        
        #Create a new thread to continuously listen for output from the Lutron SSH server
        thread1 = Thread(target = self.listenOnChannel)
        thread1.start()
        
    def initalize(self):
        self.channel.send('{"CommuniqueType":"ReadRequest","Header":{"Url":"/device"}}\n')
        time.sleep(3)
        print self.channel.recv(9999)

    def openChannel(self):
        return self.client.invoke_shell()
        
    def listenOnChannel(self):
        while not self.channel.exit_status_ready():
            print "Listening"
            # Only print data if there is data to read in the channel
            output = self.channel.recv(9999)
            print output
            
            notifyDevices(output)
            
    def send(self, cmd):
        print "sending cmd" + cmd
        self.channel.send(cmd)
        

'''
class MyListener(object):

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        global SMARTBRIDGE_IP
        info = zeroconf.get_service_info(type, name)
        #print ipaddress.IPv4Address(info.address)
        SMARTBRIDGE_IP = "192.168.1.47" #str(ipaddress.IPv4Address(info.address))
'''

def notifyDevices(output):

    if SMARTTHINGS_IP:
        body = json.dumps(output)
        host = 'http://' + SMARTTHINGS_IP + ':39500'
        agent = Agent(reactor)
        req = agent.request(
            'POST',
            host,
            Headers({'Content-Type': ['application/json'], 'CONTENT-LENGTH': [str(len(output))]}),
            StringProducer(output)
            )
    else: 
        print ("Something is wrong, you'r ST hub wasn't found\nRun the Caseta Service Manager to get started")
    
def proBridgeSetup():
    global PRO_BRIDGE
    if PRO_BRIDGE == True:
        return
    try:
        telnet = smartBridgeTELNET(SMARTBRIDGE_IP) 
        PRO_BRIDGE = True
    except:
        print "There was an error connecting to your Pro Bridge. Did you turn Telnet on in the Lutron app?"


'''         
def saveData():
    print "Saving Data"
    f = open('savedIP', "w")
    f.write("SMARTTHINGS_IP:" + SMARTTHINGS_IP + "\n")
    f.write("PRO_BRIDGE:" + str(PRO_BRIDGE) + "\n")
    f.close
   
def setSmartBridgeIP():
    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_lutron._tcp.local.", listener)
    while not SMARTBRIDGE_IP:
        pass
    print "Your Lutron Smart Bridge IP Address is: " + SMARTBRIDGE_IP

def startup():
    f = open('savedIP', 'r')
    global SMARTTHINGS_IP
    for line in f:
        if "SMARTTHINGS_IP" in line:
            SMARTTHINGS_IP = line.split(':')[1].strip()
            print SMARTTHINGS_IP
        elif "PRO_BRIDGE" in line:
            print line.split(':')[1]
            if line.split(':')[1].strip() == "True":
                proBridgeSetup()
            else: 
                print "You appear to have a standard bridge"
'''
    
def determine_ip_for_host(host = None):
    """Determine local IP address used to communicate with a particular host"""
    if (host == None):
        host = '192.168.1.1'
    test_sock = DatagramProtocol()
    test_sock_listener = reactor.listenUDP(0, test_sock)
    test_sock.transport.connect(host, 1900)
    my_ip = test_sock.transport.getHost().host
    test_sock_listener.stopListening()
    return my_ip
       
def main():
    
    #Please paste in the IP Address for your Lutron Smart Bridge and for your SmartThings Hub below!!
    #smartBridgeIP = "192.168.1.47" #22
    #smartThingsIP = "192.168.1.19"
    #setSmartBridgeIP()
    #startup()
    iface = determine_ip_for_host()
    obj = Client(iface)
    reactor.addSystemEventTrigger('before', 'shutdown', obj.stop)
    proBridgeSetup()
    ssh = smartBridgeSSH() 
    device_target = 'urn:schemas-upnp-org:device:RPi_Lutron_Caseta:%d' % (1)
    status_site = server.Site(StatusServer(device_target, ssh))
    reactor.listenTCP(5000, status_site) # pylint: disable=no-member
    

if __name__ == "__main__":

    reactor.callWhenRunning(main)
    reactor.run()
