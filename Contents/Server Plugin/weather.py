#! /usr/bin/env python
# -*- coding: utf-8 -*-

import xmltodict

ERROR_DEFAULT = 999.9

class Observation:
	def __init__(self,doc):
		self.data = doc['siteData']['currentConditions']
		self.timestamp = self.data['dateTime'][0]['timeStamp']
		self.currentConditions = CurrentConditions(self.data)
		self.yesterdayConditions = YesterdayConditions(doc['siteData']['yesterdayConditions'])

class CurrentConditions:
	def __init__(self,xml):
		self.xml = xml
		self.condition = self.xml['condition']
		self.temperature = float(self.xml.get('temperature', {}).get('#text',ERROR_DEFAULT))
		self.tempString = "{0}°C".format(self.temperature) if self.temperature != ERROR_DEFAULT else "NA"

		self.dewpoint = float(self.xml.get('dewpoint', {}).get('#text',ERROR_DEFAULT))
		self.dewpointString = "{0}°C".format(self.dewpoint) if self.dewpoint != ERROR_DEFAULT else "NA"

		self.humidity = float(self.xml.get('relativeHumidity', {}).get('#text',ERROR_DEFAULT))
		self.pressure = float(self.xml.get('pressure', {}).get('#text',999.9))

		self.visibility = float(self.xml.get('visibility', {}).get('#text',999.9))
		self.winds = Winds(self.xml['wind'])

class Winds:
	def __init__(self,xml):
		self.xml = xml
		self.windSpeed = int(self.xml['speed']['#text'])
		self.windDirection = self.xml['direction']

		#	sometimes a bearing is not provided
		#	so use an error bearing of 999.9
		self.windBearing = float(self.xml.get('bearing', {}).get('#text',999.9))
		self.windGust = int(self.xml.get('gust', {}).get('#text',0))

class YesterdayConditions:
	def __init__(self,xml):
		self.xml = xml
		temp1 = float(self.xml.get('temperature', {})[0].get('#text',999.9))
		temp2 = float(self.xml.get('temperature', {})[1].get('#text',999.9))
		self.yesterdayHigh = max(temp1,temp2)
		self.yesterdayLow = min(temp1,temp2)
		self.yesterdayPrecip = float(self.xml.get('precip', {}).get('#text',999.9))

class TodayForecast:
	"""Forecast for today"""
	def __init__(self,doc):
		self.xml = doc
		#	drill down to today's forecast, the 1st in the fc group
		fcxml = self.xml['siteData']['forecastGroup']['forecast'][0]
