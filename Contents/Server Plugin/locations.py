# -*- coding: utf-8 -*-
import xmltodict
import urllib2
import sqlite3
import weather
import indigo

class LocationDatabase:
	def __init__(self):
		try:
			response = urllib2.urlopen('http://dd.weatheroffice.ec.gc.ca/citypage_weather/xml/siteList.xml')
		except urllib2.HTTPError, e:
			errMsg = "HTTP error obtaining Environment Canada station list: {0}".format(str(e))
			indigo.server.log(errMsg,isError=True)
			return
		doc = xmltodict.parse(response)
		self.conn = sqlite3.connect(':memory:')
		self.cursor = self.conn.cursor()
		self.cursor.execute('CREATE TABLE sites (code text, location text, province text)')
		for siteXML in doc['siteList']['site']:
			code = siteXML['@code']
			loc = siteXML['nameEn']
			province = siteXML['provinceCode']

			insert = "INSERT INTO sites VALUES(?, ?, ?)"
			self.cursor.execute(insert, (code,loc, province))

	def provinces(self):
		self.cursor.execute('SELECT DISTINCT province FROM sites ORDER BY province')
		return self.cursor.fetchall()

	def stationsForProvice(self,province):
		if province is "":
			self.cursor.execute('SELECT code,location,province FROM sites ORDER BY province')
		else:
			self.cursor.execute("SELECT code,location, province FROM sites WHERE province=? ORDER BY location",(province,))
		return self.cursor.fetchall()

	def provinceLocs(self,provinceCode):
		sql = "SELECT location FROM sites WHERE province='%s' ORDER BY location" % provinceCode
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def locationCode(self,provinceCode,location):
		self.cursor.execute("SELECT code FROM sites WHERE province=? AND location=? LIMIT 1",(provinceCode,location))
		return self.cursor.fetchone()[0]

	# def locationWx(self,provinceCode,location):
	# 	locationCode = self.locationCode(provinceCode, location)
	# 	encodedLoc = locationCode.encode('utf-8')
	# 	url = "http://dd.weatheroffice.ec.gc.ca/citypage_weather/xml/%s/%s_e.xml" % (provinceCode, encodedLoc)
	# 	response = urllib2.urlopen(url)
	# 	doc = xmltodict.parse(response)
	# 	return doc

class Location:
	def __init__(self,code,province):
		self.locationCode = code
		self.provinceCode = province

		#	construct URL and read the current weather for this site
		self.url = "http://dd.weather.gc.ca/citypage_weather/xml/{0}/{1}_e.xml".format(self.provinceCode,self.locationCode)
		self.update()

	def update(self):
		try:
			response = urllib2.urlopen(self.url)
		except urllib2.HTTPError, e:
			errMsg = "HTTP error updating station {0}: {1}".format(self.locationCode,str(e))
			indigo.server.log(errMsg,isError=True)
			return
		doc = xmltodict.parse(response)

		#	obtain a current observation object with the data
		self.currentObservation = weather.CurrentObservation(doc)
		#	obtain a forecast for today's weather
		self.forecastToday = weather.TodayForecast(doc)
		#	yesterday's weather data
		self.yesterdayWeather = weather.YesterdayConditions(doc)
