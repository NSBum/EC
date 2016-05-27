# -*- coding: utf-8 -*-
import indigo
import indigoPluginUtils
import locations
import weather
import re

class Plugin(indigo.PluginBase):
	"""Top-level class for the pluginId

	Attributes:
		deviceList (array): A list of devices owned by this plugin.
		locationDB (LocationDatabase): The sqlite database used to store information about Canadian locations.
	"""

	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.mylogger = indigoPluginUtils.logger(self)
		self.debug = False
		self.deviceList = []
		self.locationDB = locations.LocationDatabase()

	def __del__(self):
		indigo.PluginBase.__del__(self)

	def startup(self):
		self.debugLog(u"startup called")

	def shutdown(self):
		self.debugLog(u"shutdown called")

	def deviceStartComm(self, device):
		self.debugLog("Starting device: " + device.name)
		if device.id not in self.deviceList:
			self.update(device)
			self.deviceList.append(device.id)
			device.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensor)

	def deviceStopComm(self, device):
		self.debugLog("Stopping device: " + device.name)
		if device.id in self.deviceList:
			self.deviceList.remove(device.id)

	def runConcurrentThread(self):
		self.debugLog("Starting concurrent tread")
		try:
			while True:
				# we sleep (30 minutes) first because when the plugin starts, each device
				# is updated as they are started.
				self.sleep(30 * 60)
				# now we cycle through each station
				for deviceId in self.deviceList:
					# call the update method with the device instance
					self.update(indigo.devices[deviceId])
		except self.StopThread:
			pass

	def update(self,device):
		"""Updates a single device owned by this plugin.

		Args:
			device (indigo.dev): The plugin device to update.
		"""
		self.debugLog("Updating device: " + device.name)

		#	create a location object for this device
		stationID = device.pluginProps["address"]
		province = device.pluginProps["province"]
		l = locations.Location(stationID, province)
		# 	and update
		l.update()

		#	update our custom states
		device.updateStateOnServer(key="observationDate", value=l.currentObservation.timestamp)
		device.updateStateOnServer(key="currentCondition", value=l.currentObservation.condition)
		device.updateStateOnServer(key="temperature", value=l.currentObservation.temperature)
		device.updateStateOnServer(key="dewpoint", value=l.currentObservation.dewpoint)
		device.updateStateOnServer(key="temperatureString", value=l.currentObservation.tempString)

		#	current winds
		device.updateStateOnServer(key="windSpeed", value=l.currentObservation.windSpeed)
		device.updateStateOnServer(key="windDirection", value=l.currentObservation.windDirection)
		device.updateStateOnServer(key="windBearing", value=l.currentObservation.windBearing)
		device.updateStateOnServer(key="windGust", value=l.currentObservation.windGust)

		#	update yesterday's weather states
		device.updateStateOnServer(key="yesterdayHighTemp", value=l.yesterdayWeather.yesterdayHigh)
		device.updateStateOnServer(key="yesterdayLowTemp", value=l.yesterdayWeather.yesterdayLow)
		device.updateStateOnServer(key="yesterdayPrecipitation", value=l.yesterdayWeather.yesterdayPrecip)

	def validateDeviceConfigUi(self, valuesDict, typeId, devId):
		self.selectedProvince = valuesDict['province']
		rawLocation = valuesDict['location']
		match = re.search("\((.+)\)", rawLocation)
		#	update hidden field "stationID"
		valuesDict['address'] = match.group(1)

		indigo.server.log(valuesDict['address'])
		return (True, valuesDict)

	def listProvinces(self, filter="", valuesDict=None, typeId="", targetId=0):
		"""Dynamic list method for provinces."""
		provinceTuples = []
		for prov in self.locationDB.provinces():
			option = prov[0].encode('utf-8')
			provinceTuples.append((option,option))
		return provinceTuples

	def listStations(self, filter="", valuesDict=None, typeId="", targetId=0):
		"""Dynamic list method for stations/cities."""
		locations = []
		stations = []
		self.debugLog(u"Generating stations")
		try:
			province = valuesDict["province"]
		except:
			province = ""
		stations = self.locationDB.stationsForProvice(province)
		for loc in stations:
			city,option = loc[1].encode('utf-8'),loc[0].encode('utf-8')
			stationName = "{0} ({1})".format(city,option)
			locations.append(stationName)
		return locations

	def provinceChanged(self, valuesDict, typeId, devId):
		"""Callback method when the province was changed by the user."""
		indigo.server.log("selectedProvince = {0}".format(valuesDict['province']))

		return valuesDict
