# -*- coding: utf-8 -*-
import xmltodict
import urllib2
import sqlite3

class CurrentObservation:
	"""Current weather observations"""
	def __init__(self,doc):
		self.xml = doc
		data = self.xml['siteData']['currentConditions']
		self.timestamp = data['dateTime'][0]['timeStamp']
		self.condition = data['condition']
		self.temperature = float(data['temperature']['#text'])
		self.tempString = "{0}°C".format(self.temperature)

		self.dewpoint = float(data['dewpoint']['#text'])
		self.dewpointString = "{0}°C".format(self.dewpoint)

		try:
			self.pressure = float(data['pressure']['#text'])
		except:
			self.pressure = 999.9
		self.visibility = float(data['visibility']['#text'])

		wind = data['wind']
		self.windSpeed = int(wind['speed']['#text'])
		self.windDirection = wind['direction']

		#	sometimes a bearing is not provided
		#	so use an error bearing of 999.9
		try:
			self.windBearing = float(wind['bearing']['#text'])
		except:
			self.windBearing = 999.9

		try:
			self.windGust = int(wind['gust']['#text'])
		except:
			self.windGust = 0

		#forecastToday = data['forecastGroup']['forecast'][0]
		#self.precipToday = int(forecastToday['abbreviatedForecast']['pop']['#text'])

class YesterdayConditions:
	"""Yesterday weather conditions"""
	def __init__(self,doc):
		data = doc['siteData']['yesterdayConditions']
		temp1,temp2 = float(data['temperature'][0]['#text']),float(data['temperature'][1]['#text'])
		self.yesterdayHigh = max(temp1,temp2)
		self.yesterdayLow = min(temp1,temp2)
		self.yesterdayPrecip = float(data['precip']['#text'])

class TodayForecast:
	"""Forecast for today"""
	def __init__(self,doc):
		self.xml = doc
		#	drill down to today's forecast, the 1st in the fc group
		fcxml = self.xml['siteData']['forecastGroup']['forecast'][0]
