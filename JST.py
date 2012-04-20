# -*- coding: utf-8 -*-
import datetime
import sys

class JST(datetime.tzinfo):
	def utcoffset(self,dt):
		return datetime.timedelta(hours=9)
	def dst(self,dt):
		return datetime.timedelta(0)
	def tzname(self,dt):
		return "JST"
