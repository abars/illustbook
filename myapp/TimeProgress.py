#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#経過時間を取得する
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import datetime
import sys

from myapp.UTC import UTC
from myapp.JST import JST

class TimeProgress():
	@staticmethod
	def get_date_str(value):
		tmp=value.replace(tzinfo=UTC()).astimezone(JST())
		return ""+str(tmp.year)+"/"+str(tmp.month)+"/"+str(tmp.day)

	@staticmethod
	def get_date_diff_str(value,footer):
		delta_time=datetime.datetime.today()-value
		if(delta_time.days>=7):
			return TimeProgress.get_date_str(value)
		if(delta_time.days>=1):
			return ""+str(delta_time.days)+"日"+footer
		if(delta_time.seconds>=60*60):
			return ""+str(delta_time.seconds/60/60)+"時間"+footer
		if(delta_time.seconds>=60):
			return ""+str(delta_time.seconds/60)+"分"+footer
		return ""+str(delta_time.seconds)+"秒"+footer
