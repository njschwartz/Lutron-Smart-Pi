metadata {
        definition (name: "Lutron Virtual Switch", namespace: "njschwartz", author: "Nate Schwartz") {
        capability "Switch"
        capability "Refresh"
        capability "Switch Level"
    }

	// simulator metadata
	simulator {
	}

	// UI tile definitions
	tiles {
		standardTile("button", "device.switch", width: 2, height: 2, canChangeIcon: true) {
			state "off", label: 'Off', action: "switch.on", icon: "st.Kids.kid10", backgroundColor: "#ffffff", nextState: "on"
			state "on", label: 'On', action: "switch.off", icon: "st.Kids.kid10", backgroundColor: "#79b821", nextState: "off"
		}
		standardTile("refresh", "device.switch", inactiveLabel: false, decoration: "flat") {
			state "default", label:'', action:"refresh.refresh", icon:"st.secondary.refresh"
		}        
		main(["button"])
		details(["button", "refresh"])
	}
}

def parse(description) {
    sendEvent(name: description.name, value: description.value)

}

def on() {
    log.debug getDataValue("zone")
    parent.setLevel(this, 100)
	sendEvent(name: "switch", value: "on")
	log.info "Switch On"
}

def off() {
	parent.off(this)
	sendEvent(name: "switch", value: "off")
	log.info "Dimmer Off"
}

def refresh() {
	log.info "refresh"
    parent.refresh(this)
}