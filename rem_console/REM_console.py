#!/usr/bin/python3

import rem_backend.query_data as qd
import rem_backend.propagation_model_estimation as pm
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

def main():
	run = 1;
	while (run):
		print("Please choose from the selection:")
		print("1. WiFi device localization")
		print("2. Duty cycle calculation")
		print("3. Path loss model estimation")
		print("0. Quit")
		choice = input(" >>  ")
		if (choice == '0'): 
			run = 0	
		elif (choice == '1'):
			print("Loc:Enter the channel of interest")
			chann = input(" >>  ")
			dev_list = qd.get_all_active_devices_on_channel(chann,1)
			try:
				print("Select the index of the device of interest")
				ind = 1
				for row in dev_list:
					print("{}. {}".format(ind,row[0]))
					ind += 1
				devind = input(" >>  ")
				print(dev_list[int(devind)-1][0])

				try:
					location = qd.estimate_tx_location(str(dev_list[int(devind)-1][0]),10)
					print("The location of devices {} is:".format(str(dev_list[int(devind)-1][0])))
					print("x:{} y:{} z:{} Pt:{} dBm".format(location[0],location[1],location[2],location[3]))
				except:
					print("not sufficient data for modeling")
					print("")
			except:
				print("no devices")
				print("")

		elif (choice == '2'): 
			print("DC:Enter the channel of interest")
			chann = input(" >>  ")
			ux, ul, dx, dy = input("provide ux ul dx dl coordinates of interest: ").split(' ')
			try:
				val = qd.get_duty_cycle_by_area(chann,10,ux,ul,dx,dy)
				dc = val[0][0]
				print("Duty cycle value for channel={} is {}".format(chann,dc))
			except:
				print("not sufficient data for modeling")
				print("")
		elif (choice == '3'): 
			print("PL:Enter the channel of interest")
			chann = input(" >>  ")
			try:
				val = pm.get_chann_model(10,chann)
				print(val)
			except:
				print("not sufficient data for modeling")
				print("")

if __name__=="__main__":
	main()
				

