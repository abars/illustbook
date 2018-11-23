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

import template_select
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

		#オーナーをカウントしない場合は弾く
		if(bbs.dont_count_owner and owner):
			return

		#カウンターを進める
		headers={'X-AppEngine-FailFast' : 'true'} #新規インスタンスの作成の抑制

		#add sync
		try:
			taskqueue.add(url="/counter_worker",params={"bbs":str(bbs.key())},queue_name="counter",headers=headers)
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
		
		#カウンタを更新
		counter=bbs.counter
		counter.update_counter()


