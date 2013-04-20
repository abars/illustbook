#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#更新情報系の公開API
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

from django.utils import simplejson

webapp.template.register_template_library('templatetags.django_filter')

from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.MesThread import MesThread
from myapp.MappingId import MappingId
from myapp.Bbs import Bbs
from myapp.BbsConst import BbsConst
from myapp.Bookmark import Bookmark
from myapp.AddBookmark import AddBookmark
from myapp.ApiObject import ApiObject
from myapp.Ranking import Ranking

class ApiFeed(webapp.RequestHandler):

#-------------------------------------------------------------------
#feed class
#-------------------------------------------------------------------

	@staticmethod
	def invalidate_cache():
		offset=0
		mode=["bookmark","new","moper","hot","applause"]
		count=[16,18,BbsConst.PINTEREST_PAGE_UNIT]
		for m in mode:
			for c in count:
				memcache.delete(ApiFeed._get_cache_id(m,None,offset,c))
	
	@staticmethod
	def _get_cache_id(order,bbs_id,offset,limit):
		if(not order):
			order="none"
		if(not bbs_id):
			bbs_id="none"
		return BbsConst.OBJECT_CACHE_HEADER+"_"+order+"_"+bbs_id+"_"+str(offset)+"_"+str(limit)
	
	@staticmethod
	def _get_query(order):
		query=db.Query(MesThread,keys_only=True)
		if(order=="bookmark"):
			query.order("-bookmark_count")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		if(order=="new"):
			query.order("-create_date")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		if(order=="applause"):
			query.order("-applause")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		if(order=="moper"):
			query.order("-applause")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_MOPER)
		if(not order):
			query.order("-create_date")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		return query
		
	@staticmethod
	def feed_get_thread_list(req,order,offset,limit):
		#最大取得数
		if(limit>100):
			limit=100

		#キャッシュが有効かどうか
		cache_enable=0
		if(offset==0):
			cache_enable=1
		
		#更新されたときにページ間で不整合が発生するために無効化
		if(order=="bookmark" or order=="applause"):
			cache_enable=0

		#キャッシュ取得
		cache_id=ApiFeed._get_cache_id(order,req.request.get("bbs_id"),offset,limit)
		if(cache_enable):
			data=memcache.get(cache_id)
		else:
			data=None
		if(data and cache_enable):
			return data
		
		#スレッド一覧取得
		if(order=="hot"):
			rank=Ranking.get_by_key_name(BbsConst.THREAD_RANKING_KEY_NAME)
			if(rank==None):
				rank=Ranking.get_or_insert(BbsConst.THREAD_RANKING_KEY_NAME)
			thread_list=rank.get_rank(offset,limit)
			bbs_id=None
		else:
			query=ApiFeed._get_query(order)

			bbs_id=None
			if(req.request.get("bbs_id")):
				bbs_key=MappingId.mapping(req.request.get("bbs_id"))
				if(bbs_key==""):
					return None #bbs not found
				query.filter("bbs_key =",db.get(bbs_key))
				bbs_id=True

			thread_list=query.fetch(offset=offset,limit=limit)
		
		#リスト作成
		dic=ApiObject.create_thread_object_list(req,thread_list,bbs_id)

		#キャッシュに乗せる
		if(cache_enable):
			memcache.set(cache_id,dic,BbsConst.TOPPAGE_FEED_CACHE_TIME)
		
		return dic

#-------------------------------------------------------------------
#main
#-------------------------------------------------------------------

	def get(self):
		SetUtf8.set()
		if(ApiObject.check_api_capacity(self)):
			return
		dic=ApiFeed.get_core(self)
		ApiObject.write_json_core(self,dic)

	@staticmethod
	def get_core(self):
		#パラメータ取得
		method=""
		if(self.request.get("method")):
			method=self.request.get("method");
		
		user_id=""
		if(self.request.get("user_id")):
			user_id=self.request.get("user_id")
		
		#返り値
		dic={"method":method}

		#フィードクラス
		if(method=="getThreadList"):
			offset=0
			if(self.request.get("offset")):
				try:
					offset=int(self.request.get("offset"))
				except:
					return {"status":"failed","message":"offset must be integer"}
			limit=10
			if(self.request.get("limit")):
				try:
					limit=int(self.request.get("limit"))
				except:
					return {"status":"failed","message":"limit must be integer"}
			order=self.request.get("order")
			dic=ApiFeed.feed_get_thread_list(self,order,offset,limit)
			if(dic==None):
				return {"status":"failed","message":"bbs not found"}
			#return {"status":"failed","message":"debug error message"}

		dic=ApiObject.add_json_success_header(dic)
		return dic
		

