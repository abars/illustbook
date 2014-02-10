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
	def get_date_diff_str(value,footer,is_english):
		day="日"
		hour="時間"
		minutes="分"
		sec="秒"
		if(is_english):
			day=" day"
			hour=" hour"
			minutes=" min"
			sec=" sec"
		if isinstance(value,str):
			return value
		delta_time=datetime.datetime.today()-value
		if(delta_time.days>=7):
			return TimeProgress.get_date_str(value)
		if(delta_time.days>=1):
			return ""+str(delta_time.days)+day+footer
		if(delta_time.seconds>=60*60):
			return ""+str(delta_time.seconds/60/60)+hour+footer
		if(delta_time.seconds>=60):
			return ""+str(delta_time.seconds/60)+minutes+footer
		return ""+str(delta_time.seconds)+sec+footer
