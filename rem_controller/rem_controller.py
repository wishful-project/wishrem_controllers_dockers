from uniflex.core import modules
from uniflex.core import events
from rem_events.rem_events import *
from datetime import date, datetime, timedelta
import time
import logging
import rem_backend.query_data as query_data
import rem_backend.insert_query as insert_data
import rem_backend.propagation_model_estimation as pm_estimation
import json

__author__ = "Daniel Denkovski, Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{danield, valentin}@feit.ukim.edu.mk"

'''
REM global controller for WISH-I-VE-A-REM 
Connects to database and performs REM processing
'''

class REMController(modules.ControlApplication):
	def __init__(self):
		'''
		Initialization of the REM global controller
		'''
		super(REMController, self).__init__()
		self.log = logging.getLogger('REMController')
		self.running = False

	@modules.on_start()
	def my_start_function(self):
		'''
		Starts the REM controller module		
		'''
		self.log.info("start REM control app")
		self.running = True

	@modules.on_exit()
	def my_stop_function(self):
		'''
		Stops the REM controller module		
		'''
		self.log.info("stop REM control app")
		self.running = False

	def get_device(self, mac_add):
		'''
		Returs information for a specific device 
		Args:
			mac_add: Mac address of the device
		Returns:
			result: Dictionary of device information. (channel capabilities, location, mode of operation, status, channel)
		'''
		result = query_data.get_device(mac_addr)
		if result is not None:
			return result
		else:
			return None

	def get_pathloss_model(self, channel):
		'''
		Returs the path loss model for a specific channel 
		Args:
			channel: the channel of interest
		Returns:
			result: Dictionary of channel_model. (L0, alpha, sigma, d0)
		'''
		result = query_data.get_pathloss_model(channel)

		if result['L0'] != 'none':
			return result
		else:
			return None 

	def get_tx_locations(self, channel, floor, timespan):
		'''
		Returs the tx locations for a specific channel floor and timespan
		Args:
			channel: the channel of interest
			floor: the floor of interest
			timespan: the timespan of interest
		Returns:
			result: List of location tupples. (mac address, x and y coordinates, global location id, tx power)
		'''
		
		result = query_data.get_tx_locations(channel, floor, timespan)
		
		if not result:
			return None
		else:
			return result 

	def get_channel_status(self, channel, threshold, timespan):
		'''
		Returs the channel status for a specific channel and timespan. Efectively cooperative spectrum sensing based on hard decision combining
		Args:
			channel: the channel of interest
			threshold: duty cycle threshold
			timepsan: the timespan of interest
		Returns:
			result: channel status (0--> free, 1--> ocupied)
		'''
		result =  query_data.get_channel_status(channel, threshold, timespan)
		if result is not None:
			return result
		else:
			return None 

	def get_channel_status_by_area(self, channel, threshold, timespan, ulx=0, uly=1000, drx=1000, dry=0):
		'''
		Returs the channel status for a specific channel, area and timespan. Efectively cooperative spectrum sensing based on hard decision combining
		Args:
			channel: the channel of interest
			threshold: duty cycle threshold
			timepsan: the timespan of interest
			ulx, uly, drx, dry: upper left and lower right corner coordinates, of the area of interest
		Returns:
			result: channel status (0--> free, 1--> ocupied)
		'''
		result = query_data.get_channel_status_by_area(channel, threshold, timespan, ulx, uly, drx, dry)
		if result is not None:
			return result
		else:
			return None
		
	def get_channel_status_by_device(self, channel, rx_add, threshold, timespan):
		'''
		Returs the channel status for a specific channel, device and timespan. 
		Args:
			channel: the channel of interest
			rx_add: mac addres of the device
			threshold: duty cycle threshold
			timepsan: the timespan of interest
		Returns:
			result: channel status (0--> free, 1--> ocupied)
		'''
		result = query_data.get_channel_status_by_device(channel, rx_add, threshold, timespan)
		if result is not None:
			return result
		else:
			return None

	def get_channel_status_all_by_device(self, rx_add, threshold, timespan):
		'''
		Returs the list of channel status for all channels, specific device and timespan.
		Args:
			rx_add: the channel of interest
			threshold: duty cycle threshold
			timepsan: the timespan of interest
		Returns:
			result: list of tuple (channel, channel status) (0--> free, 1--> ocupied)
		'''	
		result = query_data.get_channel_status_all_by_device(rx_add, threshold, timespan)
		if not result:
			return None
		else:
			return result

	def get_channel_status_all(self, threshold, timespan):
		'''
		Returs the list of channel status for all channels, and timespan. Efectively cooperative spectrum sensing based on hard decision combining 
		Args:
			threshold: duty cycle threshold
			timepsan: the timespan of interest
		Returns:
			result: list of tuple (channel, channel status) (0--> free, 1--> ocupied)
		'''
		result = query_data.get_channel_status_all(threshold, timespan)
		if not result:
			return None
		else:
			return result

	def get_duty_cycle(self, channel, timespan):
		'''
		Returs the duty cycle for a channel and timespan of interest
		Args:
			channel: channel of interest
			timepsan: the timespan of interest
		Returns:
			result: the duty cycle value
		'''
		result =  query_data.get_duty_cycle(channel, timespan)
		if result is not None:
			return result
		else:
			return None

	def get_duty_cycle_by_area(self, channel, timespan, ulx=0, uly=1000, drx=1000, dry=0):
		'''
		Returs the duty cycle for a channel, area and timespan of interest
		Args:
			channel: channel of interest
			timepsan: the timespan of interest
			ulx, uly, drx, dry: upper left and lower right corner coordinates, of the area of interest
		Returns:
			result: the duty cycle value
		'''
		result =  query_data.get_duty_cycle_by_area(channel, timespan, ulx, uly, drx, dry)
		if not result:
			return None
		else:
			return result

	def get_duty_cycle_by_device(self, channel, rx_add, timespan):
		'''
		Returs the duty cycle for a channel, device and timespan of interest
		Args:
			channel: channel of interest
			rx_add: the mac address of the device
			timepsan: the timespan of interest
		Returns:
			result: the duty cycle value
		'''
		result =  query_data.get_duty_cycle_by_device(channel, rx_add, timespan)
		if not result:
			return None
		else:
			return result

	def get_duty_cycle_all_channels_by_device(self, rx_add, timespan):
		'''
		Returs the duty cycle for all channels, for a given device and timespan of interest
		Args:
			rx_add: the mac address of the device
			timepsan: the timespan of interest
		Returns:
			result: list of tupple (channel,duty cycle)
		'''
		result =  query_data.get_duty_cycle_all_channels_by_device(rx_add, timespan)
		if not result:
			return None
		else:
			return result

	def get_duty_cycle_all_channels(self, timespan):
		'''
		Returs the duty cycle for all channels, and timespan of interest
		Args:
			timepsan: the timespan of interest
		Returns:
			result: list of tupple (channel,duty cycle)
		'''
		result =  query_data.get_duty_cycle_all_channels(timespan)
		if not result:
			return None
		else:
			return result

	def get_duty_cycle_heat_map(self, channel, timespan, nx=50, ny=50, ulx=0, uly=1000, drx=1000, dry=0, intp=1):
		'''
		Returs the duty cycle heatmap for a specific channel, area and timespan of interest
		Args:
			channel: the channel of interest
			timepsan: the timespan of interest
			ulx, uly, drx, dry: upper left and lower right corner coordinates, of the area of interest
			nx,ny: grid resolution of heat map
			intp: interpolation type. Please check interpoaltion module for more information
		Returns:
			result: vector of calculated/interpolated values
		'''
		result =  query_data.get_duty_cycle_heat_map(channel, timespan, nx, ny, ulx, uly, drx, dry, intp)
		if result is not None:
			return result
		else:
			return None

	def estimate_tx_location(self, addr, timespan=60, ulx=0, uly=15, drx=32, dry=0, nx=50, ny=50, nz=50):
		'''
		Returs the estimated location of a tx of interest
		Args:
			addr: the mac address of the localized device
			timepsan: the timespan of interest
			ulx, uly, drx, dry: upper left and lower right corner coordinates, of the area of interest
			nx,ny,nz: grid resolution of the localization algorithm
		Returns:
			result: tuple consisted of estimated x,y,z coordinates and respective estimated tx power (x,y,z,txpow)
		'''
		result =  query_data.estimate_tx_location(addr, timespan, ulx, uly, drx, dry, nx, ny, nz)
		if result is not None:
			return result
		else:
			return None

	def estimate_tx_range(self, addr, timespan=60):
		'''
		Returs the estimated tx range of a tx of interest
		Args:
			addr: the mac address of the localized device
			timepsan: the timespan of interest
		Returns:
			val: dictionary with 2 points in 3D space (xmin,ymin,zmin,xmax,ymax,zmax)
		'''
		result =  query_data.estimate_tx_range(addr, timespan)
		if result is not None:
			return result
		else:
			return None		

	def get_occupied_channels(self):
		result =  query_data.get_occupied_channels()
		if not result:
			return None
		else:
			return result

	def get_occupied_channels_count(self):	
		result =  query_data.get_occupied_channels_count()
		if not result:
			return None
		else:
			return result	

	def get_ap_statistics(self, timespan=1):
		result =  query_data.get_ap_statistics(timespan)
		if not result:
			return None
		else:
			return result	

	def get_ap_degraded_retries(self, timespan=1, retries_threshold=10):
		result =  query_data.get_ap_degraded_retries(timespan, retries_threshold)	
		if not result:
			return None
		else:
			return result	

	def get_all_active_devices_on_channel(self, chann, timespan=10):
		result =  query_data.get_all_active_devices_on_channel(chann, timespan)	
		if not result:
			return None
		else:
			return result

	def get_chann_model(self, timespan, chann):
		'''
		get the model L0, exp, sigma on a given channel (reference distance d0 = 1m)
		Args:
			timespan: the timespan of interest
			chann: the channel of interest
		
		Returns:
			data: dictionary of the path loss L0, exp, sigma 
		'''
		return pm_estimation.get_chann_model(timespan, chann)

	def insert_device_location(self, macaddr, locx, locy, locz, locid, floor, loc_type = 0):
		'''
		Inserts device location in the database
		Args:
			macaddr: the mac address of the device
			locx, locy, locz: x, y, z locations
			locid: the id of the global location
			floor: the floor the device is on
			loc_type: 0-> fixed, 1->estimated
		'''
		device_data = (macaddr, locx, locy, locz, locid, floor, loc_type)
		insert_data.insert_device_location(data_device)

	def device_init(self):
		'''
		Sets all devices to inactive
		'''
		insert_data.device_init()

	def insert_device_capabilities(self, macaddr, uuid, capab):
		'''
		Inserts device capabilities in the database
		Args:
			macaddr: the mac address of the device
			uuid: the uuid of the node
			capab: dictionary with capabilities
		'''
		capab_str = json.dumps(capab)
		device_data = (macaddr, uuid, capab_str)
		insert_data.insert_device_capabilities(device_data)

	def update_device_status(self, macaddr, status, hw_mode = None, power = None, ssid = None, channel = None, sec_channel = None, apmac = None):
		'''
		Inserts device status in the database
		Args:
			macaddr: the mac address of the device
			status: status of the device (-1->off, 0->idle, 1->monitor, 2->ap, 3->station)
			hw_mode: needed for AP mode (a, b, g, n)
			power: transmit power of the device
			ssid: ssid of the AP
			channel: the used channel
			sec_channel: the used (if) secondary channel (802.11n mode)
			apmac: mac address of the AP (for station mode config)
		'''
		device_data = (macaddr, status, hw_mode, power, ssid, channel, sec_channel, apmac)
		insert_data.update_device_status(device_data)

	def insert_duty_cycle(self, rmac, dc, chnel):
		'''
		Inserts duty cycle information in the database
		Args:
			rmac: the receiver mac address
			dc: duty cycle value (absolute, not in percent)
			chnel: channel number
		'''
		dc_data = (rmac, dc*100, datetime.now(), chnel)
		insert_data.insert_duty_cycle(dc_data)

	def insert_tx_location(self, tx_mac_address, x_coord, y_coord, global_loc_id, floor, channel, tx_power):
		'''
		Inserts localized tx information in the database
		Args:
			tx_mac_address: the transmitter mac address
			x_coord, y_coord: the x and y coordinates of the transmitter
			global_loc_id: the id of the global location
			floor: the floor of the device
			channel: the used channel
			tx_power: the estimated transmit power
		'''
		location_data = (tx_mac_address, x_coord, y_coord, global_loc_id, floor, datetime.now(), channel, tx_power)
		insert_data.insert_tx_location(location_data)

	def insert_propagation_model(self, L0, alpha, sigma, channel):
		'''
		Inserts propagation model information in the database
		Args:
			L0, exp, sigma on a given channel (reference distance d0 = 1m)
		'''
		data = (str(L0), str(alpha), str(sigma), 1, datetime.now(), channel) 
		insert_data.insert_propagation_model(data)

	def insert_rssi_measurement(self, tx_mac_address, rx_mac_address, rssi, channel):
		'''
		Inserts rssi measurement information in the database
		Args:
			tx_mac_address: the transmitter mac address
			rx_mac_address: the receiver mac address
			rssi: sensed rssi value
			channel: the used channel
		'''
		data = (tx_mac_address, rx_mac_address, rssi, datetime.now(), 'data', 1, channel, 0)
		insert_data.insert_rssi_measurement(data)

	def insert_global_location(self, name, locx, locy, locz):
		'''
		Inserts global location information in the database
		Args:
			name: the name of the global location
			locx, locy, locz: x, y, z coordinates
		'''
		location_data = (name, locx, locy, locz)
		locid = insert_data.insert_global_location(location_data)
		return locid

	def insert_ap_statistics(self, apmac, tot_ret, tot_fai, tot_tx_thr, tot_rx_thr, tot_tx_act, tot_rx_act):
		'''
		Inserts AP statistics information in the database
		Args:
			apmac: the mac address of the AP
			tot_ret: total tx packet retries decimal (0 to 1)
			tot_fai: total tx packet failed decimal (0 to 1)
			tot_tx_thr: achieved total tx throughput in Mbps
			tot_rx_thr: achieved total rx throughput in Mbps
			tot_tx_act: total tx activity decimal (0 to 1)
			tot_rx_act: total rx activity decimal (0 to 1)
		'''
		ap_data = (apmac, tot_ret*100, tot_fai*100, tot_tx_thr/1000000, tot_rx_thr/1000000, tot_tx_act*100, tot_rx_act*100, datetime.now())
		insert_data.insert_ap_statistics(ap_data)

	def insert_link_statistics(self, txmac, rxmac, rssi, tx_ret, tx_fai, tx_rate, rx_rate, tx_thr, rx_thr, tx_act, rx_act):
		'''
		Inserts link statistics information in the database
		Args:
			txmac: the transmitter MAC address
			rxmac: the receiver MAC address
			rssi: rssi value (in dBm)
			tx_ret: tx packet retries decimal (0 to 1)
			tx_fai: tx packet failed decimal (0 to 1)
			tx_rate: used tx_rate in Mbps
			rx_rate: used rx_rate in Mbps
			tx_thr: achieved tx throughput in Mbps
			rx_thr: achieved rx throughput in Mbps
			tx_act: tx activity decimal (0 to 1)
			rx_act: rx activity decimal (0 to 1)
		'''
		link_data = (txmac, rxmac, rssi, tx_ret*100, tx_fai*100, tx_rate/1000000, rx_rate/1000000, tx_thr/1000000, rx_thr/1000000, tx_act*100, rx_act*100, datetime.now())
		insert_data.insert_link_statistics(link_data)

	@modules.on_event(REMGetDeviceInformationEvent)
	def serve_get_device_event(self, event):
		macaddress = event.macaddress
		result = get_device(macaddress)
		if result is not None:
			rsp_event = REMRspDeviceInformationEvent(macaddress, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetPathlossModel)
	def serve_get_pathloss_model_event(self, event):
		channel = event.channel
		result = get_pathloss(channel)
		if result is not None:
			rsp_event = REMRspPathlossModel(channel, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetTransmittersLocations)
	def serve_get_tx_locations_event(self, event):
		channel = event.channel
		floor = event.floor
		timespan = event.timespan
		result = get_tx_locations(channel, floor, timespan)
		if result is not None:
			rsp_event = REMRspTransmittersLocations(channel, floor, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetChannelStatus)
	def serve_get_channel_status_event(self, event):
		channel = event.channel
		threshold = event.threshold
		timespan = event.timespan
		result = get_channel_status(channel, threshold, timespan)
		if result is not None:
			rsp_event = REMRspChannelStatus(channel, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetChannelStatusByArea)
	def serve_get_channel_status_by_area_event(self, event):
		channel = event.channel
		threshold = event.threshold
		timespan = event.timespan
		ulx = event.ulx
		uly = event.uly
		drx = event.drx
		dry = event.dry
		result = get_channel_status_by_area(channel, threshold, timespan, ulx, uly, drx, dry)
		if result is not None:
			rsp_event = REMRspChannelStatusByArea(channel, ulx, uly, drx, dry, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetChannelStatusByDevice)
	def serve_get_channel_status_by_device_event(self, event):
		channel = event.channel
		threshold = event.threshold
		timespan = event.timespan
		rx_addr = event.rx_addr
		result = get_channel_status_by_device(channel, rx_add, threshold, timespan)
		if result is not None:
			rsp_event = REMRspChannelStatusByDevice(channel, rx_add, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetAllChannelsStatusByDevice)
	def serve_get_channel_status_all_by_device_event(self, event):
		rx_addr = event.rx_addr
		threshold = event.threshold
		timespan = event.timespan
		result = get_channel_status_all_by_device(rx_add, threshold, timespan)
		if result is not None:
			rsp_event = REMRspAllChannelsStatusByDevice(rx_add, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetAllChannelsStatus)
	def serve_get_channel_status_all_event(self, event):
		threshold = event.threshold
		timespan = event.timespan
		result = get_channel_status_all(threshold, timespan)
		if result is not None:
			rsp_event = REMRspAllChannelsStatus(result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetDutyCycle)
	def serve_get_duty_cycle_event(self, event):
		channel = event.channel
		timespan = event.timespan
		result = get_duty_cycle(channel, timespan)
		if result is not None:
			rsp_event = REMRspDutyCycle(channel, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetDutyCycleByArea)
	def serve_get_duty_cycle_by_area_event(self, event):
		channel = event.channel
		timespan = event.timespan
		ulx = event.ulx
		uly = event.uly
		drx = event.drx
		dry = event.dry
		result = get_duty_cycle_by_area(channel, timespan, ulx, uly, drx, dry)
		if result is not None:
			rsp_event = REMRspDutyCycleByArea(channel, ulx, uly, drx, dry, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetDutyCycleByDevice)
	def serve_get_duty_cycle_by_device_event(self, event):
		channel = event.channel
		rx_add = event.rx_add
		timespan = event.timespan
		result = get_duty_cycle_by_device(channel, rx_add, timespan)
		if result is not None:
			rsp_event = REMRspDutyCycleByDevice(channel, rx_add, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetDutyCycleAllChannelsByDevice)
	def serve_get_duty_cycle_all_channels_by_device_event(self, event):
		timespan = event.timespan
		rx_add = event.rx_add
		result = get_duty_cycle_all_channels_by_device(rx_add, timespan)
		if result is not None:
			rsp_event = REMRspDutyCycleAllChannelsByDevice(rx_add, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetDutyCycleAllChannels)
	def serve_get_duty_cycle_all_channels_event(self, event):
		timespan = event.timespan
		result = get_duty_cycle_all_channels(timespan)
		if result is not None:
			rsp_event = REMRspDutyCycleAllChannels(result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetDutyCycleHeatMap)
	def serve_get_duty_cycle_heat_map_event(self, event):
		timespan = event.timespan
		channel = event.channel
		ulx = event.ulx
		uly = event.uly
		drx = event.drx
		dry = event.dry
		nx = event.nx
		ny = event.ny
		result = get_duty_cycle_heat_map(channel, timespan, nx, ny, ulx, uly, drx, dry)
		if result is not None:
			rsp_event = REMRspDutyCycleHeatMap(channel, result)
			self.send_event(rsp_event)
	
	@modules.on_event(REMGetEstimatedTXLocation)
	def serve_estimate_tx_location_event(self, event):
		addr = event.addr
		timespan = event.timespan
		uly = event.ulx
		uly = event.uly
		drx = event.drx
		dry = event.dry
		nx = event.nx
		ny = event.ny
		nz = event.nz
		result = estimate_tx_location(addr, timespan, ulx, uly, drx, dry, nx, ny, nz)
		if result is not None:
			rsp_event = REMRspEstimatedTXLocation(addr, result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetOccupiedChannels)
	def serve_get_occupied_channels_event(self, event):
		result = get_occupied_channels()
		if result is not None:
			rsp_event = REMRspOccupiedChannels(result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetOccupiedChannelsCount)
	def serve_get_occupied_channels_count_event(self, event):
		result = get_occupied_channels_count()
		if result is not None:
			rsp_event = REMRspOccupiedChannelsCount(result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetAllAPStatistics)
	def serve_get_ap_statistics_event(self, event):
		result = get_ap_statistics(event.timespan)
		if result is not None:
			rsp_event = REMRspAllAPStatistics(result)
			self.send_event(rsp_event)

	@modules.on_event(REMGetDegradedAPsBasedOnRetries)
	def serve_get_ap_degraded_retries_event(self, event):
		result = get_ap_degraded_retries(event.timestamp, event.retries_threshold)
		if result is not None:
			rsp_event = REMRspDegradedAPs(results)
			self.send_event(rsp_event)

	@modules.on_event(REMGetAllActiveDevicesOnChannel)
	def serve_get_all_active_devices_on_channel_event(self, event):
		channel = event.channel
		timespan = event.timespan
		result = get_all_active_devices_on_channel(channel, timespan)
		if result is not None:
			rsp_event = REMRspAllActiveDevicesOnChannel(channel, result)
			self.send_event(rsp_event)

	@modules.on_event(REMCalculatePathLossModel)
	def serve_get_all_active_devices_on_channel_event(self, event):
		channel = event.channel
		timespan = event.timespan
		result = get_chann_model(timespan, channel)
		if result is not None:
			rsp_event = REMRspPathlossModel(channel, result)
			self.send_event(rsp_event)

