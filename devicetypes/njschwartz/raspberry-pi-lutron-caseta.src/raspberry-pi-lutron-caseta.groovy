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
    definition (name: "Raspberry Pi Lutron Caseta", namespace: "njschwartz", author: "Nate Schwartz") {
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
  log.debug msg
  def bodyString = msg.body
  if (bodyString) {
    def json = msg.json
    
  log.debug json
    
    //Send all data to the parent parse method for event generation
    if (json) {
    	parent.parse(json) 
      log.debug "Values received: ${json}"
    }
  }
}

def sync(ip, port) {
    def existingIp = getDataValue("ip")
    def existingPort = getDataValue("port")
    if (ip && ip != existingIp) {
        updateDataValue("ip", ip)
    }
    if (port && port != existingPort) {
        updateDataValue("port", port)
    }
}
