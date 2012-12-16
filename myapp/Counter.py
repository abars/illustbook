#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#カウンターシステム
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.BbsConst import BbsConst

import datetime

class Counter(db.Model):
	#カウンター
	total_cnt=db.IntegerProperty(indexed=False)
	today_cnt=db.IntegerProperty(indexed=False)
	yesterday_cnt=db.IntegerProperty(indexed=False)
	yesterday_yesterday_cnt=db.IntegerProperty(indexed=False)
	
	#カウンター更新判定用
	today_date=db.IntegerProperty(indexed=False)
	#ip = db.StringProperty(indexed=False)
	
	#最後に更新された日
	update_date = db.DateProperty(auto_now=True,indexed=False)
	
	def init_cnt(self) :
		self.total_cnt = 0
		self.today_cnt = 0
		self.yesterday_cnt = 0
		self.yesterday_yesterday_cnt = 0
	
	@staticmethod
	def is_same_ip(remote_addr,bbs):
		cache_id=BbsConst.OBJECT_COUNTER_IP_HEADER+str(bbs.key())
		before_ip=memcache.get(cache_id)
		if(before_ip==remote_addr):
			return True
		memcache.set(cache_id,remote_addr,BbsConst.COUNTER_IP_CACHE_TIME)
		return False

	@staticmethod
	def reset_ip(bbs):
		cache_id=BbsConst.OBJECT_COUNTER_IP_HEADER+str(bbs.key())
		memcache.delete(cache_id)
		
	def update_counter(self,remote_addr,dont_count_owner):
		#カウンターを更新
		if(not dont_count_owner):
			self.total_cnt=self.total_cnt+1
			self.today_cnt=self.today_cnt+1
			self.put()
		
		#1日を超えていた場合
		now = datetime.datetime.today()+datetime.timedelta(hours=9)
		now_date=now.day+now.month*12+now.year*365
		if(now_date!=self.today_date):
			self.yesterday_yesterday_cnt=self.yesterday_cnt
			self.yesterday_cnt=self.today_cnt-1
			self.today_cnt=1
			self.today_date=now_date
			self.put()

