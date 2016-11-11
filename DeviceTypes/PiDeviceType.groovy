/**
 *  Raspberry Pi Lutron Caseta Device Type
 *
 *  Copyright 2015 Richard L. Lynch <rich@richlynch.com>
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 *  in compliance with the License. You may obtain a copy of the License at:
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
 *  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
 *  for the specific language governing permissions and limitations under the License.
 *
 */

metadata {
    definition (name: "Raspberry Pi Lutron Caseta", namespace: "smartthings", author: "Nate Schwartz") {
        capability "Contact Sensor"
        capability "Polling"
        capability "Refresh"
    }

    simulator {
    }

   	tiles(scale: 2) {
     	multiAttributeTile(name:"mainTile"){
			tileAttribute ("", key: "PRIMARY_CONTROL") {
	            attributeState "default", label: "Lutron Pi", action: "", icon: "st.Lighting.light99-hue", backgroundColor: "#F3C200"
			}
	        tileAttribute ("networkAddress", key: "SECONDARY_CONTROL") {
	            attributeState "default", label:'IP: ${currentValue}'
			}
            }
            		valueTile("networkAddress", "device.networkAddress", decoration: "flat", height: 1, width: 4, inactiveLabel: false) {
			state "default", label:'IP: ${currentValue}'
		}
	main (["mainTile"])
		details(["mainTile", "networkAddress"])
	}
}

// parse events into attributes
def parse(description) {
  def msg = parseLanMessage(description)
  def bodyString = msg.body
  if (bodyString) {
    def json = msg.json
    
    //Send all data to the parent parse method for event generation
    if (json) {
    	parent.parse(json) 
      log.debug "Values received: ${json}"
      //Can do stuff here in need be
    }
  }
}
 
 
/* 
private Integer convertHexToInt(hex) {
    Integer.parseInt(hex,16)
}

private String convertHexToIP(hex) {
    [convertHexToInt(hex[0..1]),convertHexToInt(hex[2..3]),convertHexToInt(hex[4..5]),convertHexToInt(hex[6..7])].join(".")
}

private getHostAddress() {
    def ip = getDataValue("ip")
    def port = getDataValue("port")

    if (!ip || !port) {
        def parts = device.deviceNetworkId.split(":")
        if (parts.length == 2) {
            ip = parts[0]
            port = parts[1]
        } else {
            //log.warn "Can't figure out ip and port for device: ${device.id}"
        }
    }

    //convert IP/port
    ip = convertHexToIP(ip)
    port = convertHexToInt(port)
    log.debug "Using ip: ${ip} and port: ${port} for device: ${device.id}"
    return ip + ":" + port
}

def getRequest(path) {
    log.debug "Sending request for ${path} from ${device.deviceNetworkId}"

    new physicalgraph.device.HubAction(
        'method': 'GET',
        'path': path,
        'headers': [
            'HOST': getHostAddress(),
        ], device.deviceNetworkId)
}

def poll() {
    log.debug "Executing 'poll' from ${device.deviceNetworkId} "

    subscribeAction(getDataValue("ssdpPath"))
}

def refresh() {
    log.debug "Executing 'refresh'"

    //def path = getDataValue("ssdpPath")
    //getRequest(path)
    subscribeAction(getDataValue("ssdpPath"))
}

def subscribe() {
    log.debug "Subscribe requested"
    log.debug getDataValue("ssdpPath")
    subscribeAction(getDataValue("ssdpPath"))
}

private def parseDiscoveryMessage(String description) {
    def device = [:]
    def parts = description.split(',')
    parts.each { part ->
        part = part.trim()
        if (part.startsWith('devicetype:')) {
            def valueString = part.split(":")[1].trim()
            device.devicetype = valueString
        } else if (part.startsWith('mac:')) {
            def valueString = part.split(":")[1].trim()
            if (valueString) {
                device.mac = valueString
            }
        } else if (part.startsWith('networkAddress:')) {
            def valueString = part.split(":")[1].trim()
            if (valueString) {
                device.ip = valueString
            }
        } else if (part.startsWith('deviceAddress:')) {
            def valueString = part.split(":")[1].trim()
            if (valueString) {
                device.port = valueString
            }
        } else if (part.startsWith('ssdpPath:')) {
            def valueString = part.split(":")[1].trim()
            if (valueString) {
                device.ssdpPath = valueString
            }
        } else if (part.startsWith('ssdpUSN:')) {
            part -= "ssdpUSN:"
            def valueString = part.trim()
            if (valueString) {
                device.ssdpUSN = valueString
            }
        } else if (part.startsWith('ssdpTerm:')) {
            part -= "ssdpTerm:"
            def valueString = part.trim()
            if (valueString) {
                device.ssdpTerm = valueString
            }
        } else if (part.startsWith('headers')) {
            part -= "headers:"
            def valueString = part.trim()
            if (valueString) {
                device.headers = valueString
            }
        } else if (part.startsWith('body')) {
            part -= "body:"
            def valueString = part.trim()
            if (valueString) {
                device.body = valueString
            }
        }
    }

    device
}

private subscribeAction(path, callbackPath="") {
	log.debug "Subscribe Action"
    def address = device.hub.getDataValue("localIP") + ":" + device.hub.getDataValue("localSrvPortTCP")
    def parts = device.deviceNetworkId.split(":")
    def ip = convertHexToIP(getDataValue("ip"))
    def port = convertHexToInt(getDataValue("port"))
    ip = ip + ":" + port
    
    log.debug path + " " + ip + " " + address

    def result = new physicalgraph.device.HubAction(
        method: "SUBSCRIBE",
        path: path,
        headers: [
            HOST: ip,
            CALLBACK: "<http://${address}/notify$callbackPath>",
            NT: "upnp:event",
            TIMEOUT: "Second-3600"])
    result
}
*/
