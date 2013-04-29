#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#カウンターのワーカー、taskqueueでカウントアップする
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

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

from myapp.Bbs import Bbs
from myapp.Counter import Counter
from myapp.Alert import Alert
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.OwnerCheck import OwnerCheck
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.BbsConst import BbsConst
from myapp.MesThread import MesThread
from myapp.PageGenerate import PageGenerate
from myapp.RecentCommentCache import RecentCommentCache
from myapp.Analyze import Analyze
from myapp.Entry import Entry
from myapp.CssDesign import CssDesign
from myapp.ApiObject import ApiObject
from myapp.Ranking import Ranking

class CounterWorker(webapp.RequestHandler):
	@staticmethod
	def update_counter(req,bbs,thread,owner):
		#同じIPからのアクセスは弾く
		remote_addr=req.request.remote_addr
		if(Counter.is_same_ip(remote_addr,bbs)):
			return

		#オーナーをカウントしないモードの判定
		dont_count=0
		if(bbs.dont_count_owner and owner):
			dont_count=1

		#リファラを取得
		url=req.request.url
		referer=Analyze.get_request_referer(req.request)

		#スレッドのKeyを取得
		thread_key=""
		if(thread):
			thread_key=str(thread.key())

		#カウンターを進める
		headers['X-AppEngine-FailFast'] = 'true' #新規インスタンスの作成の抑制
		try:
			taskqueue.add(url="/counter_worker",params={"bbs":str(bbs.key()),"thread":thread_key,"dont_count":str(dont_count),"referer":referer,"url":url,"remote_addr":remote_addr},queue_name="counter",headers=headers)
		except:
			logging.warning("counter taskqueue add failed")

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

		#カウンタを更新
		counter=bbs.counter
		counter.update_counter(remote_addr,dont_count)

		#オーナーをカウントしないモードでオーナーだった場合は終了
		if(dont_count):
			return

		#ランキング用のPVをカウント
		if(thread):
			Ranking.add_rank_global(thread,BbsConst.SCORE_PV)

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

