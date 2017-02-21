#! /usr/bin/env python
# -*- coding: utf-8 -*-

class Station:
    """An Environment Canada reporting site
    """
	def __init__(self,province,stationID):
		self.prov = province
		self.addr = stationID
	def url(self):
		return "http://dd.weather.gc.ca/citypage_weather/xml/{0}/{1}_e.xml".format(self.prov,self.addr)
