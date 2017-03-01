/**
 *  Copyright 2015 SmartThings
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
	definition (name: "Lutron Pico On/Off", namespace: "njschwartz", author: "Stephan Hackett")  {
		capability "Actuator"
		capability "Button"
		capability "Sensor"

        command "push1"
        command "push2"
        command "push4"
	}

	
	tiles (scale: 2) {
		standardTile("button", "device.button", width: 2, height: 2, canChangeIcon: true, canChangeBackground: true){
			state "default", label: "", icon: "st.unknown.zwave.remote-controller", backgroundColor: "#ffffff"
		}
 		standardTile("push1", "device.button", width: 1, height: 1, decoration: "flat") {
			state "default", label: "Push 1", backgroundColor: "#ffffff", action: "push1"
		}
 		standardTile("push2", "device.button", width: 4, height: 2, decoration: "flat") {
			state "default", label: "2", icon: "st.Lighting.light11", backgroundColor: "#ffffff", action: "push2"
		}
 		standardTile("push4", "device.button", width: 4, height: 2, decoration: "flat") {
			state "default", label: "4", icon: "st.Lighting.light13", backgroundColor: "#ffffff", action: "push4"
		} 		
 		standardTile("blank", "device.button", width: 2, height: 2, decoration: "flat") {
			state "default", label: "", backgroundColor: "#ffffff"
		}
 		

		main "button"
		details(["push2","button","push4"])
	}
}

def parse(description) {
	log.debug description.data.buttonNumber
    buttonEvent(description.data.buttonNumber)
}

def buttonEvent(button) {
	button = button as Integer
    log.debug "In button event " + button
    createEvent(name: "button", value: "pushed", data: [buttonNumber: button], descriptionText: "$device.displayName button $button was pushed", isStateChange: true)
}

def push1() {
	push(1)
}

def push2() {
	push(2)
}

def push4() {
	push(4)
}

private push(button) {
	log.debug "$device.displayName button $button was pushed"
	sendEvent(name: "button", value: "pushed", data: [buttonNumber: button], descriptionText: "$device.displayName button $button was pushed", isStateChange: true)
}

def installed() {
	initialize()
}

def updated() {
	initialize()
}

def initialize() {
	sendEvent(name: "numberOfButtons", value: 3)
}