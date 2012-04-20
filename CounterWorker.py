#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#カウンターワーカー

import cgi
import os
import sys
import re
import datetime
import random
import logging
import urllib

from google.appengine.api.labs import taskqueue

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from Bbs import Bbs
from Counter import Counter
from Alert import Alert
from MappingId import MappingId
from SetUtf8 import SetUtf8
from OwnerCheck import OwnerCheck
from MaintenanceCheck import MaintenanceCheck
from BbsConst import BbsConst
from MesThread import MesThread
from PageGenerate import PageGenerate
from RecentCommentCache import RecentCommentCache
from Analyze import Analyze
from Entry import Entry
from CssDesign import CssDesign
from ApiObject import ApiObject

class CounterWorker(webapp.RequestHandler):
	@staticmethod
	def update_counter(req,bbs,thread,owner):
		dont_count=0
		if(bbs.dont_count_owner and owner):
			dont_count=1
		url=req.request.url
		referer=Analyze.get_request_referer(req.request)
		remote_addr=req.request.remote_addr
		thread_key=""
		if(thread):
			thread_key=str(thread.key())
		taskqueue.add(url="/counter_worker",params={"bbs":str(bbs.key()),"thread":thread_key,"dont_count":str(dont_count),"referer":referer,"url":url,"remote_addr":remote_addr},queue_name="counter")
	
	def post(self):
		#BBS取得
		bbs_key=self.request.get("bbs")
		bbs=None
		if(bbs_key):
			bbs=ApiObject.get_cached_object(str(bbs_key))
		if(not bbs):
			return
		
		#スレッド情報を取得（タイトル取得用）
		thread_key=self.request.get("thread")
		thread=None
		if(thread_key):
			thread=ApiObject.get_cached_object(str(thread_key))
		
		#カウントしないモードかどうか
		dont_count=int(self.request.get("dont_count"))

		#リファラを取得
		referer=self.request.get("referer")
		url=self.request.get("url")
		remote_addr=self.request.get("remote_addr")
		
		#カウンタ更新
		CounterWorker.update_counter_core(bbs,bbs_key,thread,dont_count,referer,url,remote_addr)
	
	@staticmethod
	def update_counter_core(bbs,bbs_key,thread,dont_count,referer,url,remote_addr):
		#カウンター取得
		counter=bbs.counter
		
		#カウンタを更新
		updated_counter=counter.update_counter(remote_addr,dont_count)
		if(dont_count):
			return
		if(not updated_counter):
			return

		#アクセス解析で表示する名前
		analyze_name=bbs.bbs_name
		if(thread):
			analyze_name=thread.title

		#アクセス解析インスタンスが存在しなかったら作成
		if(not bbs.analyze):
			#キャッシュされていないBBSを取得
			bbs=db.get(bbs_key)
			
			#インスタンス作成
			analyze=Analyze()
			analyze.init_analyze(bbs)
			analyze.put()
			bbs.analyze=analyze
			bbs.put()
		
		#アクセス解析更新
		analyze=bbs.analyze
		analyze.add_referer(referer,url,analyze_name)


