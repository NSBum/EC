#! /usr/bin/env python
# -*- coding: utf-8 -*-

import indigo
import indigoPluginUtils
import re
import urllib2
from weather import *
from station import Station

ERROR_DEFAULT = 999.9

def updateVar(name, value, folder=0):
	if name not in indigo.variables:
		indigo.variable.create(name, value=value, folder=folder)
	else:
		indigo.variable.updateValue(name, value)


class Plugin(indigo.PluginBase):
	"""Top-level class for the pluginId
	"""

	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.mylogger = indigoPluginUtils.logger(self)
		self.debug = False
		self.deviceList = []

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

	def goToStationURL(self, valuesDict, typeId, devId):
		self.browserOpen("http://dd.weather.gc.ca/citypage_weather/docs/site_list_towns_en.csv")

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

		#	construct the url to fetch xml
		addr = device.pluginProps["address"]
		province = device.pluginProps["province"]
		station = Station(province,addr)
		#	try to fetch station xml
		try:
			response = urllib2.urlopen(station.url())
		except urllib2.HTTPError, e:
			errMsg = "HTTP error updating station {0}: {1}".format(addr,str(e))
			indigo.server.log(errMsg,isError=True)
			return
		except Exception, e:
			self.errorLog("Unknown error getting station %s data: %s" % (addr, str(e)))
			return
		doc = xmltodict.parse(response)
		obs = Observation(doc)
		device.updateStateOnServer(key="observationDate", value=obs.timestamp)
		device.updateStateOnServer(key="currentCondition", value=obs.currentConditions.condition)
		device.updateStateOnServer(key="temperature", value=obs.currentConditions.temperature)
		device.updateStateOnServer(key="temperatureString", value=obs.currentConditions.tempString)
		device.updateStateOnServer(key="dewpoint", value=obs.currentConditions.dewpoint)
		device.updateStateOnServer(key="dewpointString", value=obs.currentConditions.dewpointString)
		device.updateStateOnServer(key="humidity", value=obs.currentConditions.humidity)
		device.updateStateOnServer(key="pressure", value=obs.currentConditions.pressure)
		device.updateStateOnServer(key="visibility", value=obs.currentConditions.visibility)
		device.updateStateOnServer(key="windSpeed", value=obs.currentConditions.winds.windSpeed)
		device.updateStateOnServer(key="windDirection", value=obs.currentConditions.winds.windDirection)
		device.updateStateOnServer(key="windBearing", value=obs.currentConditions.winds.windBearing)
		device.updateStateOnServer(key="windGust", value=obs.currentConditions.winds.windGust)
		device.updateStateOnServer(key="yesterdayHighTemp", value=obs.yesterdayConditions.yesterdayHigh)
		device.updateStateOnServer(key="yesterdayLowTemp", value=obs.yesterdayConditions.yesterdayLow)
		device.updateStateOnServer(key="yesterdayPrecipitation", value=obs.yesterdayConditions.yesterdayPrecip)

	def validateDeviceConfigUi(self, valuesDict, typeId, devId):
		stationID = valuesDict['address'].encode('ascii','ignore').lower()
		province = valuesDict['province'].encode('ascii','ignore').upper()
		station = Station(province,stationID)
		indigo.server.log(station.url())
		try:
			urllib2.urlopen(station.url())
		except urllib2.HTTPError, e:
			errorsDict = indigo.Dict()
			errorsDict['address'] = "Station not found or isn't responding"
			self.errorLog("Error getting station %s data: %s" % (stationID, str(e)))
			return (False, valuesDict, errorsDict)
		indigo.server.log(valuesDict['address'])
		return (True, valuesDict)
