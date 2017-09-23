from uniflex.core import modules
from rem_events.sensing_events import *
from rem_events.rrm_events import *
from uniflex.core.timer import TimerEventSender
from datetime import date, datetime, timedelta
import time
import logging
import math
import random as rd
import numpy as np
#import rem_backend.query_data as qd
import json

__author__ = "Daniel Denkovski, Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{danield, valentin}@feit.ukim.edu.mk"

'''
Simple RRM global controller for WISH-I-VE-A-REM 
Connects to node controller to provide RRM functionalities
Uses REM backend to find and allocate channels to APs
'''

class RRMController(modules.ControlApplication):
	def __init__(self):
		'''
		Initialization of the simple RRM global controller
		Starts a timer event for reevaluation of RRM allocations.
		'''
		super(RRMController, self).__init__()
		self.log = logging.getLogger('RRMController')
		self.running = False

		self.timeInterval = 10
		self.retries_threshold = 10
		self.timer = TimerEventSender(self, RRMEvaluationTimeEvent)
		self.timer.start(self.timeInterval)

	def reconfigure_ap(self, apmac):
		'''
		If there are available channels, the controller calculates the duty cycle at the AP location of the for all channels.
		The RRM controller allocates the AP to the channel with the lowest duty cycle value, i.e. lowest activity.
		If all channels are occupied by active access points, the RRM controller allocates the channel with least active APs.
		Sends RRMReconfigureAP to the node controller to (re)configure the AP.
		Args:
			apmac: the MAC address of the access point		
		'''
		dev = None
		remControl = self.get_rem_controller()
		if remControl is not None:
			if remControl.is_running():
				dev = remControl.blocking(True).get_device(apmac)
			#else: remControl.start()

		#dev = qd.get_device(apmac)
		if dev is not None:
			chan_capab = json.loads(dev['chan_capab'])
			ocup_chann = np.array(remControl.blocking(True).get_occupied_channels()) # get all ocupied chann
			#ocup_chann = np.array(qd.get_occupied_channels()) # get all ocupied chann

			chan_list_str = chan_capab.keys()
			chan_list = list(map(int, chan_list_str))
			all_chan = np.asarray(chan_list)
			free_chann = all_chan[np.where(np.invert(np.in1d(all_chan, ocup_chann)))[0]]
			print(free_chann)
	
			retV = 0
			candidate_chann = 0

			if (len(free_chann) > 0):
				dc_val = 100			
				for chann in np.nditer(free_chann):
					tmp = remControl.blocking(True).get_duty_cycle_heat_map(chann, 1, 1, 1, dev['x_coord'], dev['y_coord'], dev['x_coord'], dev['y_coord'])
					#tmp = qd.get_duty_cycle_heat_map(chann, 1, 1, 1, dev['x_coord'], dev['y_coord'], dev['x_coord'], dev['y_coord'])
					print(tmp)
					tmp = tmp[0][2]
					if tmp in [0, 100]:
						tmp = remControl.blocking(True).get_duty_cycle(chann, 1) # get the duty cycle for chann
						#tmp = qd.get_duty_cycle(chann, 1) # get the duty cycle for given chann
						#print(tmp)
						if tmp[0] is None:
							tmp = 100
						else:
							tmp = tmp[0]
			
					if (tmp < dc_val):
						dc_val = tmp
						candidate_chann = chann
		
				if (candidate_chann > 0):
					retV = 1
				else:
					#reconf channel to rnd id
					candidate_chann = all_chan[rd.randint(1, len(all_chan))]
					retV = 2	
			else:
				# allocate the AP to the channel with least APs. If all the same allocate to lowest channel index

				chan_info = np.asarray(remControl.blocking(True).get_occupied_channels_count())
				#chan_info = np.asarray(qd.get_occupied_channels_count())
				chan_info_new = chan_info[np.in1d(chan_info[:,1], all_chan)]
				tup = min(chan_info_new, key=lambda t: t[0])
				candidate_chann = tup[1]

				if (candidate_chann > 0):
					retV = 1
				else:
					#reconf channel to id=rnd
					candidate_chann = all_chan[rd.randint(1, len(all_chan))]
					retV = 2

			candidate_chann = int(candidate_chann)
			canchstr = str(candidate_chann)
			chentry = chan_capab[canchstr]
			power = chentry['max-tx']
			hwmod = 'g'
			if 'g' in chentry['stds']:
				hwmod = 'g'
			elif 'a' in chentry['stds']:
				hwmod = 'a'
				power = chentry['max-tx']
			htcap = None
			ssid = 'SMARTAP'
	
			self.log.info("Configuration: ap_mac = {}, ssid = {}, channel = {}, power = {}, hw_mode = {}, ht_capab = {}".format(apmac, ssid, candidate_chann, power, hwmod, htcap))
			rrmconfigure_event = RRMReconfigureAP(apmac, ssid, power, int(candidate_chann), hwmod, htcap)
			self.send_event(rrmconfigure_event)

	@modules.on_start()
	def my_start_function(self):
		'''
		Starts the RRM controller module		
		'''
		self.log.info("start RRM control app")
		self.running = True

	@modules.on_exit()
	def my_stop_function(self):
		'''
		Stops the RRM controller module		
		'''
		self.log.info("stop RRM control app")
		self.running = False
		self.timer.cancel()

	@modules.on_event(WiFiGetCapabilities)
	def serve_get_capabilities(self, event):
		'''
		Handles the WiFiGetCapabilities event.
		Sends RRMRegister event to the node controller to register.
		'''
		node = self.localNode
		if (node.uuid == event.receiverUuid):
			try:
				rrmreg_event = RRMRegister()
				self.send_event(rrmreg_event)
			except Exception as e:
				self.log.error("{} Failed, err_msg: {}".format(datetime.datetime.now(), e))

	@modules.on_event(RRMRequestAPConfiguration)
	def serve_request_ap_config(self, event):
		'''
		Handles the RRMRequestAPConfiguration event.
		Calls self.reconfigure_ap to reconfigure the AP with MAC address event.macaddr.
		'''
		node = self.localNode
		self.reconfigure_ap(event.macaddr)

	@modules.on_event(RRMEvaluationTimeEvent)
	def periodic_evaluation(self, event):
		'''
		Handles the RRMEvaluationTimeEvent event.
		Calculates the AP statistics and finds out degraded APs based on transmission retries.
		Reconfigures APs if degraded using the self.reconfigure_ap function.
		'''
		self.log.info("Periodic RRM Evaluation")

		remControl = self.get_rem_controller()
		if remControl is not None:
			if remControl.is_running():
				timeMinutes = self.timeInterval/60
				results = remControl.blocking(True).get_ap_statistics(timeMinutes)
				#results = qd.get_ap_statistics(timeMinutes)
				self.log.info("AP statistics: \n{} ".format(results))
				degraded_aps = remControl.blocking(True).get_ap_degraded_retries(timeMinutes, self.retries_threshold)
				#degraded_aps = qd.get_ap_degraded_retries(timeMinutes, self.retries_threshold)
				self.log.info("Degraded APs: \n{} ".format(degraded_aps))
				if degraded_aps is not None:
					for ap in degraded_aps:
						self.reconfigure_ap(ap[0])

		self.timer.start(self.timeInterval)

	def get_rem_controller(self):
		remControl = None
		for node in self.get_nodes():
			for app in node.get_control_applications():
				if app.name == "REMController":
					remControl = app
					break
		return remControl

	@modules.on_event(events.NewNodeEvent)
	def add_node(self, event):
		'''
		Adds a REMController node in the active node list  
		'''
		node = event.node
		for app in node.get_control_applications():
			if app.name == "REMController":
				self._add_node(node)

	@modules.on_event(events.NodeExitEvent)
	@modules.on_event(events.NodeLostEvent)
	def remove_node(self, event):
		'''
		Removes a REMController from the active node list, when it stops operating  
		'''
		node = event.node
		reason = event.reason
		if node in self.get_nodes(): self._remove_node(node)
