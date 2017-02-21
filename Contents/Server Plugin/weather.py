#! /usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict

ERROR_DEFAULT = 999.9

class CurrentObservation:
	"""Current weather observations"""
	def __init__(self,doc):
		self.xml = doc
		data = self.xml['siteData']['currentConditions']
		self.timestamp = data['dateTime'][0]['timeStamp']
		self.condition = data['condition']
		self.temperature = float(data.get('temperature', {}).get('#text',ERROR_DEFAULT))
		self.tempString = "{0}°C".format(self.temperature) if self.temperature != ERROR_DEFAULT else "NA"

		self.dewpoint = float(data.get('dewpoint', {}).get('#text',ERROR_DEFAULT))
		self.dewpointString = "{0}°C".format(self.dewpoint) if self.dewpoint != ERROR_DEFAULT else "NA"

		self.humidity = float(data.get('relativeHumidity', {}).get('#text',ERROR_DEFAULT))
		indigo.server.log(str(self.humidity))

		self.pressure = float(data.get('pressure', {}).get('#text',999.9))
		self.visibility = float(data.get('visibility', {}).get('#text',999.9))

		wind = data['wind']
		self.windSpeed = int(wind['speed']['#text'])
		self.windDirection = wind['direction']

		#	sometimes a bearing is not provided
		#	so use an error bearing of 999.9
		self.windBearing = float(wind.get('bearing', {}).get('#text',999.9))
		self.windGust = int(wind.get('gust', {}).get('#text',0))

		#forecastToday = data['forecastGroup']['forecast'][0]
		#self.precipToday = int(forecastToday['abbreviatedForecast']['pop']['#text'])

class YesterdayConditions:
	"""Yesterday weather conditions"""
	def __init__(self,doc):
		data = doc['siteData']['yesterdayConditions']
		temp1 = float(data.get('temperature', {})[0].get('#text',999.9))
		temp2 = float(data.get('temperature', {})[1].get('#text',999.9))
		self.yesterdayHigh = max(temp1,temp2)
		self.yesterdayLow = min(temp1,temp2)
		self.yesterdayPrecip = float(wind.get('precip', {}).get('#text',999.9))

class TodayForecast:
	"""Forecast for today"""
	def __init__(self,doc):
		self.xml = doc
		#	drill down to today's forecast, the 1st in the fc group
		fcxml = self.xml['siteData']['forecastGroup']['forecast'][0]
