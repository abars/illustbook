#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#JSTに変換する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import datetime
import sys

class JST(datetime.tzinfo):
	def utcoffset(self,dt):
		return datetime.timedelta(hours=9)
	def dst(self,dt):
		return datetime.timedelta(0)
	def tzname(self,dt):
		return "JST"
