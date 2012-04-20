#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#カウンターシステム
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

import datetime

class Counter(db.Model):
	total_cnt=db.IntegerProperty()
	today_cnt=db.IntegerProperty()
	yesterday_cnt=db.IntegerProperty()
	yesterday_yesterday_cnt=db.IntegerProperty()
	today_date=db.IntegerProperty()
	start_date = db.DateTimeProperty(auto_now_add=True)
	update_date = db.DateProperty(auto_now=True)
	ip = db.StringProperty()
	
	def init_cnt(self) :
		self.total_cnt = 0
		self.today_cnt = 0
		self.yesterday_cnt = 0
		self.yesterday_yesterday_cnt = 0
	
	def reset_ip(self):
		self.ip=""
		
	def update_counter(self,remote_addr,dont_count):
		updated=False
		if(remote_addr and self.ip!=str(remote_addr)):
			self.ip=str(remote_addr)
			if(not dont_count):
				self.total_cnt=self.total_cnt+1
				self.today_cnt=self.today_cnt+1
			updated=True
		now = datetime.datetime.today()+datetime.timedelta(hours=9)
		now_date=now.day+now.month*12+now.year*365
		if(now_date!=self.today_date):
			self.yesterday_yesterday_cnt=self.yesterday_cnt
			self.yesterday_cnt=self.today_cnt-1
			self.today_cnt=1
			self.today_date=now_date
			updated=True
		if(updated):
			self.put()#db.put_async(self)
		return updated





