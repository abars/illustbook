#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#イラストブック全体の統計情報
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os
import time
import sys
import urllib
import re
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import memcache

from myapp.SetUtf8 import SetUtf8
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.Alert import Alert
from myapp.NicoTracker import NicoTracker
from myapp.TopPageCache import TopPageCache
from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
from myapp.Entry import Entry
from myapp.Bookmark import Bookmark

class SiteAnalyzer(webapp.RequestHandler):
	@staticmethod
	def get_cache():
		cache=TopPageCache.get_or_insert(key_name="top_page_cache")
		return cache

	def get(self):
		SetUtf8.set()

		#キャッシュ取得
		cache=SiteAnalyzer.get_cache();

		#1日単位で習得
		force=False
		if(cache.date and len(cache.day_list)>=1 and not force):
			day1_str=NicoTracker.get_day_string(cache.date)
			day2_str=NicoTracker.get_day_string(datetime.datetime.today())
			if(day1_str==day2_str):
				self.response.out.write(Alert.alert_msg("まだ1日が経過していません。",self.request.host))
				return
		
		#コメント数と再生数を取得
		bbs_cnt=Bbs.all().count(limit=100000)
		illust_cnt=MesThread.all().count(limit=100000)
		entry_cnt=Entry.all().count(limit=100000)
		user_cnt=Bookmark.all().count(limit=100000)

		#書き込み
		day_str=NicoTracker.get_day_string(datetime.datetime.today())
		
		cache.entry_cnt_list.insert(0,entry_cnt)
		cache.illust_cnt_list.insert(0,illust_cnt)
		cache.bbs_cnt_list.insert(0,bbs_cnt)
		cache.user_cnt_list.insert(0,user_cnt)
		cache.day_list.insert(0,day_str)

		cache.bbs_n=bbs_cnt
		cache.illust_n=illust_cnt

		cache.put()

		self.response.out.write(Alert.alert_msg("ランキングを更新しました。",self.request.host))
	
	@staticmethod
	def create_graph(self,no):
		cache=SiteAnalyzer.get_cache()
		if(no==0):
			return NicoTracker.create_graph(cache.day_list,cache.bbs_cnt_list)
		if(no==1):
			return NicoTracker.create_graph(cache.day_list,cache.illust_cnt_list)
		if(no==2):
			return NicoTracker.create_graph(cache.day_list,cache.entry_cnt_list)
		if(no==3):
			return NicoTracker.create_graph(cache.day_list,cache.user_cnt_list)
		return None




