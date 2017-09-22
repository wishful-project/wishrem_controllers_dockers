#!/usr/bin/python3

from uniflex.core import modules
from uniflex.core import events
from rem_events.rem_events import *
#import rem_backend.query_data as qd
#import rem_backend.propagation_model_estimation as pm
import threading
import _thread

__author__ = "Daniel Denkovski", "Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{danield, valentin}@feit.ukim.edu.mk"

'''
REM console module
Showcases the REM backend capabilities of the extension
Used as console interface for users to interact with the platform
'''

class REMConsole(modules.ControlApplication):
	def __init__(self):
		'''
		Initialization of the global REM console controller
		'''
		super(REMConsole, self).__init__()
		self.log = logging.getLogger('REMConsole')
		self.running = False

	@modules.on_start()
	def my_start_function(self):
		'''
		Starts the REMConsole 
		'''
		self.log.info("start global REM console controller app")
		self.running = True
		mythread = threading.Thread(target=self.main_menu)
		mythread.start()

	@modules.on_exit()
	def my_stop_function(self):
		'''
		Stops the REMConsole   
		'''
		self.log.info("stop global REM console controller app")
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
			elif (choice == '1'):
				print("Loc:Enter the channel of interest")
				chann = input(" >>  ")

				dev_list = None
				remControl = self.get_rem_controller()
				if remControl is not None:
					if remControl.is_running():
						dev_list = remControl.blocking(True).get_all_active_devices_on_channel(chann,1)

				if dev_list is not None:
					print("Select the index of the device of interest")
					ind = 1
					for row in dev_list:
						print("{}. {}".format(ind,row[0]))
						ind += 1
					devind = input(" >>  ")
					print(dev_list[int(devind)-1][0])

					points = remControl.blocking(True).estimate_tx_range(str(dev_list[int(devind)-1][0]), 10)
					if points is not None:
						estimateLocEvent = REMGetEstimatedTXLocation(str(dev_list[int(devind)-1][0]), 10, points['xmin'], points['ymax'], points['xmax'], points['ymin'], 10, 10, 10)
						self.send_event(estimateLocEvent)
				else:
					print("no devices or no REM controller")
					print("")

			elif (choice == '2'): 
				print("DC:Enter the channel of interest")
				chann = input(" >>  ")
				ux, ul, dx, dy = input("provide ux ul dx dl coordinates of interest: ").split(' ')

				getDCevent = REMGetDutyCycleByArea(chann,10,ux,ul,dx,dy)
				self.send_event(getDCevent)


			elif (choice == '3'): 
				print("PL:Enter the channel of interest")
				chann = input(" >>  ")

				getPMevent = REMCalculatePathLossModel(chann,10)
				self.send_event(getPMevent)

	@modules.on_event(REMRspEstimatedTXLocation)
	def serve_rcv_estimated_tx_location_event(self, event):
		addr = event.addr
		val = event.val
		print("The location of devices {} is:".format(addr))
		print("x:{} y:{} z:{} Pt:{} dBm".format(val[0],val[1],val[2],val[3]))

	@modules.on_event(REMRspDutyCycleByArea)
	def serve_rcv_duty_cycle_by_area(self, event):
		channel = event.channel
		dc = event.dc[0][0]
		print("Duty cycle value for channel={} is {}".format(channel,dc))

	@modules.on_event(REMRspPathlossModel)
	def serve_rcv_duty_cycle_by_area(self, event):
		pl_model = event.pl_model
		channel = event.channel
		print("Propagation model for channel={} is {}".format(channel,pl_model))

