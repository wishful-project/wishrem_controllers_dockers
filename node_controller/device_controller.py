from uniflex.core import modules
import logging
#import datetime
from datetime import date, datetime, timedelta
import time
from uniflex.core import modules
from uniflex.core import events
from rem_events.sensing_events import *
from rem_events.rrm_events import *
#from uniflex.core.timer import TimerEventSender
import threading
import _thread
from random import randint
#import rem_backend.insert_query as insert_query
#import json

__author__ = "Daniel Denkovski"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{danield}@feit.ukim.edu.mk"

'''
WiFi Global DeviceController 
The node controller (i.e. device controller) is responsible for managing the active nodes, in terms of sensing and communication. It is developed as a global controller that orchestrates all active nodes in the experiment.
'''

class DeviceController(modules.ControlApplication):
	def __init__(self):
		'''
		Initialization of the global WiFi DeviceController
		'''
		super(DeviceController, self).__init__()
		self.log = logging.getLogger('DeviceController')
		self.mynodes = {}
		self.myrrm_uuid = None
		self.running = False

	def get_rem_controller(self):
		remControl = None
		for node in self.get_nodes():
			for app in node.get_control_applications():
				if app.name == "REMController":
					remControl = app
					break
		return remControl

	def main_menu(self):
		'''
		The function manages the console application part of the controller.
		Provides the user several possibilities for interacting with the experiment i.e. active WiFi devices:
		1) It allows the user to list all active devices in the experiment. 
		2) It allows the user to configure a specific WiFi device either as an access point, station or monitor device. 
		'''
		while (self.running):
			print("Please choose from the selection:")
			print("1. List WiFi devices")
			print("2. Configure WiFi Devices")
			print("0. Quit")
			choice = input(" >>  ")
			if (choice == '0'): 
				self.running = False
				_thread.interrupt_main()
			elif (choice == '1'): self.print_nodes()
			elif (choice == '2'): 
				self.print_nodes()
				numNodes = len(self.mynodes)
				if numNodes:
					print("Which device do you want to configure? ({}-{})".format(1, numNodes))	
					pnode = input(" >>  ")
					if pnode.isdigit() and int(pnode) >= 1 and int(pnode) <= numNodes: 
						nodeind = int(pnode) - 1
						print("Make a selection (1 for monitor, 2 for AP, 3 for station)")
						pmode = input (" >>  ")
						if pmode.isdigit() and int(pnode) >= 1 and int(pnode) <= 3:
							modeind = int(pmode)
							if modeind == 1:
								uuid = list(self.mynodes.keys())[nodeind]
								node = self.mynodes[uuid]
								self.setup_wifi_monitor(node['MAC'])
							if modeind == 2:
								if self.myrrm_uuid:
									uuid = list(self.mynodes.keys())[nodeind]
									node = self.mynodes[uuid]
									macad = node['MAC']				
									rrm_request_event = RRMRequestAPConfiguration(macad)
									self.send_event(rrm_request_event)
								else:
									uuid = list(self.mynodes.keys())[nodeind]
									node = self.mynodes[uuid]
									noChs = len(node['capabilities'])
									if noChs >= 1:
										macad = node['MAC']
										ssid = 'SMARTAP'
										selId = randint(0, noChs-1)
										chnel = list(node['capabilities'])[selId]
										chentry = node['capabilities'][chnel]
										hwmod = 'g'
										if 'g' in chentry['stds']:
											hwmod = 'g'
										elif 'a' in chentry['stds']:
											hwmod = 'a'
										power = chentry['max-tx']
										htcap = None
										self.setup_wifi_ap(macad, ssid, power, chnel, hwmod, htcap)									
							if modeind == 3:
								uuid = list(self.mynodes.keys())[nodeind]
								node = self.mynodes[uuid]
								apindices = self.print_apnodes()
								if (apindices):
									print("Make a selection {}".format(apindices))
									apstr = input (" >>  ")
									if apstr.isdigit() and int(apstr) in apindices:
										apind = int(apstr) - 1
										apuuid = list(self.mynodes.keys())[apind]
										apnode = self.mynodes[apuuid]
										mymac = node['MAC']
										apmac = apnode['MAC']
										ssid = apnode['config']['ssid']
										power = apnode['config']['power']
										channel = apnode['config']['channel']
										self.setup_wifi_station(mymac, ssid, apmac, power, channel)
				else:
					print("No WiFi devices!")
					continue

	def print_nodes(self):
		'''
		Prints the information of all active WiFi devices: MAC address, capabilities, configuration and connection information.  
		'''
		print("Listing connected WIFi devices... ")
		nodeInd = 1
		for node in self.mynodes:
			mac = self.mynodes[node]['MAC']
			capabilities = self.mynodes[node]['capabilities']
			status = self.mynodes[node]['status']
			details = self.mynodes[node]['details']
			config = self.mynodes[node]['config']
			print("-> WiFi #{}: Status: {}, MAC: {} \n\tConnection: {} \n\tConfiguration: {}".format(nodeInd, status, mac, details, config))
			nodeInd += 1

	def print_apnodes(self):
		'''
		Prints the information of all controlled WiFi access point: AP’s MAC address, SSID configuration and connection info   
		'''
		print("Listing WiFi AP devices... ")
		nodeInd = 1
		apindices = []
		for node in self.mynodes:
			mac = self.mynodes[node]['MAC']
			capabilities = self.mynodes[node]['capabilities']
			status = self.mynodes[node]['status']
			details = self.mynodes[node]['details']
			config = self.mynodes[node]['config']
			if status == 'AP':
				print("-> AP #{}: MAC: {}, Configuration: {}".format(nodeInd, mac, config))
				apindices.append(nodeInd)
			nodeInd += 1
		return apindices

	@modules.on_start()
	def my_start_function(self):
		'''
		Starts the WiFi DeviceController   
		'''
		self.log.info("start global WiFi controller app")
		self.running = True
		mythread = threading.Thread(target=self.main_menu)
		#mythread.daemon = True
		mythread.start()

		remControl = self.get_rem_controller()
		if remControl is not None:
			if remControl.is_running():
				remControl.blocking(True).device_init()
			#else: remControl.start()
		#insert_query.device_init()

	@modules.on_exit()
	def my_stop_function(self):
		'''
		Stops the WiFi DeviceController   
		'''
		self.log.info("stop global WiFi controller app")
		self.running = False

	@modules.on_event(events.NewNodeEvent)
	def add_node(self, event):
		'''
		Adds a new node in the active node list  
		'''
		node = event.node
		#self.log.info("Added new node: {}, Local: {}".format(node.uuid, node.local))
		self._add_node(node)
		try:
			getcap_event = WiFiGetCapabilities(node.uuid)				
			self.send_event(getcap_event)

		except Exception as e: {}
			#self.log.error("{} Failed, err_msg: {}".format(datetime.datetime.now(), e))

	@modules.on_event(events.NodeExitEvent)
	@modules.on_event(events.NodeLostEvent)
	def remove_node(self, event):
		'''
		Removes a node from the active node list, when it stops operating  
		'''
		#self.log.info("Node lost".format())
		node = event.node
		reason = event.reason	
		if self.myrrm_uuid == node.uuid: self.myrrm_uuid = None
		else:
			if node.uuid in self.mynodes: del self.mynodes[node.uuid]
		if self._remove_node(node): {}
			#self.log.info("Node: {}, Local: {} removed reason: {}".format(node.uuid, node.local, reason))

	@modules.on_event(WiFiRssiSampleEvent)
	def serve_rssi_sample_event(self, event):
		'''
		Handles data regarding the sensed RSSI from a WiFi device, on a given channel and stores it in the REM database  
		'''
		receiver = event.node

		remControl = self.get_rem_controller()
		if remControl is not None:
			if remControl.is_running():
				remControl.blocking(True).insert_rssi_measurement(event.ta, event.ra, event.rssi, event.chnel)
			#else: remControl.start()

		#data = (event.ta, event.ra, event.rssi, datetime.now(), 'data', 1, event.chnel, 0)
		#insert_query.insert_rssi_measurement(data)
		#self.log.info("RSSI: uuid: {}, RA: {}, TA: {}, value: {}, channel: {}".format(receiver.uuid, event.ra, event.ta, event.rssi, event.chnel))

	@modules.on_event(WiFiDutyCycleSampleEvent)
	def serve_duty_cycle_sample_event(self, event):
		'''
		Handles data regarding the sensed duty cycle from a WiFi device on a given channel and stores it in the REM database  
		'''
		receiver = event.node

		remControl = self.get_rem_controller()
		if remControl is not None:
			if remControl.is_running():
				remControl.blocking(True).insert_duty_cycle(event.ra, event.dc, event.chnel)
			#else: remControl.start()

		#dc_data = (event.ra, event.dc*100, datetime.now(), event.chnel)
		#insert_query.insert_duty_cycle(dc_data)
		#self.log.info("Duty cycle: uuid: {}, RA: {}, value: {}, channel: {}".format(receiver.uuid, event.ra, event.dc, event.chnel))

	@modules.on_event(WiFiCapabilities)
	def serve_capabilities_event(self, event):
		'''
		Handles data regarding the capabilities of a WiFi device and stores it in the REM database  
		'''
		receiver = event.node
		#self.log.info("WiFiCapabilities: uuid: {}, MAC: {}, capabilities: {}".format(receiver.uuid, event.macaddr, event.capabilities))
		self.mynodes[receiver.uuid] = {}
		self.mynodes[receiver.uuid]['MAC'] = event.macaddr
		self.mynodes[receiver.uuid]['capabilities'] = event.capabilities
		self.mynodes[receiver.uuid]['status'] = 'idle'
		self.mynodes[receiver.uuid]['details'] = ""
		self.mynodes[receiver.uuid]['config'] = {}

		remControl = self.get_rem_controller()
		if remControl is not None:
			if remControl.is_running():
				remControl.blocking(True).insert_device_capabilities(event.macaddr, receiver.uuid, event.capabilities)
			#else: remControl.start()

		#capab_str = json.dumps(event.capabilities)
		#device_data = (event.macaddr, receiver.uuid, capab_str)
		#insert_query.insert_device_capabilities(device_data)
		self.setup_wifi_monitor(event.macaddr)

	def setup_wifi_ap(self, macaddr, ssid, power, channel, hw_mode, ht_capab):
		'''
		Asks a specified active WiFi device to configure as an access point.
		Sends a WiFiConfigureAP event to the WiFi device.
		Args:
			macaddr: the MAC address of the WiFi device to be configured as AP
			ssid: the SSID of the WiFi AP
			power: the tx power of the WiFi AP
			channel: the channel of the WiFi AP
			hw_mode: the hw_mode (a,b,g,n) of the WiFi AP
			ht_capab: the ht_capab of the WiFi AP (e.g. HT40+)
		'''
		startap_event = WiFiConfigureAP(macaddr, ssid, power, channel, hw_mode, ht_capab)				
		self.send_event(startap_event)

	def setup_wifi_station(self, macaddr, ssid, ap, power, channel):
		'''
		Asks a specified active WiFi device to configure as a station.
		Sends a WiFiConfigureStation event to the WiFi device.
		Args:
			macaddr: the MAC address of the WiFi device to be configured as station
			ssid: the SSID of the WiFi AP to connect to
			ap: the MAC address of the WiFi AP to connect to
			power: the tx power of the WiFi station
			channel: the channel of the WiFi AP to connect to
		'''
		startsta_event = WiFiConfigureStation(macaddr, ssid, ap, power, channel)				
		self.send_event(startsta_event)

	def setup_wifi_monitor(self, macaddr):
		'''
		Asks a specified active WiFi device to configure as a monitor device.
		Sends a WiFiConfigureMonitor event to the WiFi device.
		Args:
			macaddr: the MAC address of the WiFi device to be configured as monitor device
		'''
		startmon_event = WiFiConfigureMonitor(macaddr)				
		self.send_event(startmon_event)

	def stop_wifi(self, macaddr):
		'''
		Asks a specified active WiFi device to stop all activities.
		Sends a WiFiStopAll event to the WiFi device.
		Args:
			macaddr: the MAC address of the WiFi device
		'''
		stop_event = WiFiStopAll(macaddr)				
		self.send_event(stop_event)

	def find_node_by_mac(self, macaddr):
		'''
		Finds WiFi node based on its MAC address
		Args:
			macaddr: the MAC address of the WiFi device
		Return: 
			self.mynodes[node] - the node object
		'''
		for node in self.mynodes:
			if self.mynodes[node]['MAC'] == macaddr:
				return self.mynodes[node]
		return None

	@modules.on_event(WiFiLinkStatistics)
	def serve_linkstats_event(self, event):
		'''
		Handles data regarding the link between a given pair of AP and station (or vice versa) and stores it in the REM database
		'''
		receiver = event.node
		txmac = event.txmac
		rxmac = event.rxmac
		rssi = event.rssi #in dBm
		tx_ret = event.tx_retries #in percents
		tx_fai = event.tx_failed #in percents
		tx_rate = event.tx_rate #in bps
		rx_rate = event.rx_rate #in bps
		tx_thr = event.tx_throughput #in bps
		rx_thr = event.rx_throughput #in bps
		tx_act = event.tx_activity #in percents
		rx_act = event.rx_activity #in percents

		remControl = self.get_rem_controller()
		if remControl is not None:
			if remControl.is_running():
				remControl.blocking(True).insert_link_statistics(txmac, rxmac, rssi, tx_ret, tx_fai, tx_rate, rx_rate, tx_thr, rx_thr, tx_act, rx_act)
			#else: remControl.start()

		#link_data = (txmac, rxmac, rssi, tx_ret*100, tx_fai*100, tx_rate/1000000, rx_rate/1000000, tx_thr/1000000, rx_thr/1000000, tx_act*100, rx_act*100, datetime.now())
		#insert_query.insert_link_statistics(link_data)

		#self.log.info("%s->%s link statistics:\n\tRSSI: %.0fdBm \n\ttx packet retries: %.2f%% \n\ttx packet fails: %.2f%% \n\ttx bitrate: %.2fMbps \n\trx bitrate: %.2fMbps \n\tachieved tx throughput: %.2fMbps \n\tachieved rx throughput: %.2fMbps \n\ttx activity: %.2f%% \n\trx activity: %.2f%%" % (txmac, rxmac, rssi, tx_ret*100, tx_fai*100, tx_rate/1000000, rx_rate/1000000, tx_thr/1000000, rx_thr/1000000, tx_act*100, rx_act*100))

	@modules.on_event(WiFiAPStatistics)
	def serve_apstats_event(self, event):
		'''
		Handles data regarding the communication status and quality between an AP and all stations that are connected to it. 
		The information is also stored in the REM database		
		'''
		receiver = event.node
		apmac = event.apmac
		stations = event.stations
		tot_ret = event.total_tx_retries #in percents
		tot_fai = event.total_tx_failed #in percents
		tot_tx_thr = event.total_tx_throughput #in bps
		tot_rx_thr = event.total_rx_throughput #in bps
		tot_tx_act = event.total_tx_activity #in percents
		tot_rx_act = event.total_rx_activity #in percents

		remControl = self.get_rem_controller()
		if remControl is not None:
			if remControl.is_running():
				remControl.blocking(True).insert_link_statistics(apmac, tot_ret, tot_fai, tot_tx_thr, tot_rx_thr, tot_tx_act, tot_rx_act)
			#else: remControl.start()

		#ap_data = (apmac, tot_ret*100, tot_fai*100, tot_tx_thr/1000000, tot_rx_thr/1000000, tot_tx_act*100, tot_rx_act*100, datetime.now())
		#insert_query.insert_ap_statistics(ap_data)

		if receiver.uuid in self.mynodes:
			self.mynodes[receiver.uuid]['details'] = "connected to {} stations: {}".format(len(stations), stations)
			self.mynodes[receiver.uuid]['stations'] = stations	

		#self.log.info("AP (%s) statistics:\n\ttotal tx packet retries: %.2f%% \n\ttotal tx packet fails: %.2f%% \n\tachieved total tx throughput: %.2fMbps \n\tachieved total rx throughput: %.2fMbps \n\ttotal tx activity: %.2f%% \n\ttotal rx activity: %.2f%%" % (apmac, tot_tx_ret*100, tot_tx_fai*100, tot_tx_thr/1000000, tot_rx_thr/1000000, tot_tx_act*100, tot_rx_act*100))

	@modules.on_event(WiFiConfigureMonitorRsp)
	def serve_configure_monitor_rsp_event(self, event):
		'''
		Handles the response from a WiFi device that was configured in monitor mode.
		Updates the device status in the REM database		
		'''
		receiver = event.node
		if receiver.uuid in self.mynodes:
			self.mynodes[receiver.uuid]['status'] = 'monitor'
			self.mynodes[receiver.uuid]['details'] = ""
			self.mynodes[receiver.uuid]['config'] = {}

			remControl = self.get_rem_controller()
			if remControl is not None:
				if remControl.is_running():
					remControl.blocking(True).update_device_status(event.macaddr, 1)

			#device_data = (event.macaddr, 1, None, None, None, None, None, None)
			#insert_query.update_device_status(device_data)
		
	@modules.on_event(WiFiConfigureStationRsp)
	def serve_configure_station_rsp_event(self, event):
		'''
		Handles the response from a WiFi device that was configured as station.
		Updates the device status in the REM database		
		'''
		receiver = event.node
		apmac = event.apmac
		staconf = event.sta_config
		if receiver.uuid in self.mynodes:
			self.mynodes[receiver.uuid]['status'] = 'station'
			self.mynodes[receiver.uuid]['details'] = "connected to BSSID: {}".format(apmac)
			self.mynodes[receiver.uuid]['config'] = staconf

			remControl = self.get_rem_controller()
			if remControl is not None:
				if remControl.is_running():
					remControl.blocking(True).update_device_status(event.macaddr, 3, None, staconf['power'], staconf['ssid'], staconf['channel'], None, apmac)

			#device_data = (event.macaddr, 3, None, staconf['power'], staconf['ssid'], staconf['channel'], None, apmac)
			#insert_query.update_device_status(device_data)
			
	@modules.on_event(WiFiConfigureAPRsp)
	def serve_apconnection_rsp_event(self, event):
		'''
		Handles the response from a WiFi device that was configured as access point.
		Updates the device status in the REM database		
		'''
		receiver = event.node
		apconf = event.ap_config
		if receiver.uuid in self.mynodes:
			self.mynodes[receiver.uuid]['status'] = 'AP'
			self.mynodes[receiver.uuid]['config'] = apconf

			if 'stations' in self.mynodes[receiver.uuid]:
				stations = self.mynodes[receiver.uuid]['stations']
				for staind in range(0, len(stations)):
					stamac = stations[staind]
					if self.find_node_by_mac(stamac) is not None:
						ssid = apconf['ssid']
						power = apconf['power']
						channel = apconf['channel']
						apmac = self.mynodes[receiver.uuid]['MAC']
						self.setup_wifi_station(stamac, ssid, apmac, power, channel)

			remControl = self.get_rem_controller()
			if remControl is not None:
				if remControl.is_running():
					remControl.blocking(True).update_device_status(event.macaddr, 2, apconf['hw_mode'], apconf['power'], apconf['ssid'], apconf['channel'])

			#device_data = (event.macaddr, 2, apconf['hw_mode'], apconf['power'], apconf['ssid'], apconf['channel'], None, None)
			#insert_query.update_device_status(device_data)

	@modules.on_event(RRMRegister)
	def serve_rrm_register_event(self, event):
		'''
		Listens for any active RRM controller in the platform and establishes connections with it.
		Uses the registered RRM controller to (re)configure APs.		
		'''
		print("RRMRegister")
		receiver = event.node
		self.myrrm_uuid = receiver.uuid

	@modules.on_event(RRMReconfigureAP)
	def serve_rrm_reconfigure_ap_event(self, event):
		'''
		Receives RRM reconfiguration messages from the RRM controller and reconfigures the WiFi AP accordingly.	
		'''
		self.setup_wifi_ap(event.macaddr, event.ssid, event.power, event.channel, event.hw_mode, event.ht_capab)

