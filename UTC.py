# -*- coding: utf-8 -*-
import datetime
import sys

class UTC(datetime.tzinfo):
	def utcoffset(self, dt):
		return datetime.timedelta(0)
	def tzname(self, dt):
		return "UTC"
	def dst(self, dt):
		return datetime.timedelta(0)
