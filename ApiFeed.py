#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#
# WEB API

import cgi
import os
import sys
import re
import datetime

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

from SetUtf8 import SetUtf8
from Alert import Alert
from MesThread import MesThread
from MappingId import MappingId
from ApplauseCache import ApplauseCache
from Bbs import Bbs
from BbsConst import BbsConst
from Bookmark import Bookmark
from AddBookmark import AddBookmark
from ApiObject import ApiObject

class ApiFeed(webapp.RequestHandler):

#-------------------------------------------------------------------
#feed class
#-------------------------------------------------------------------

	@staticmethod
	def invalidate_cache():
		offset=0
		memcache.delete(ApiFeed._get_cache_id("bookmark",None,offset))
		memcache.delete(ApiFeed._get_cache_id("new",None,offset))
		memcache.delete(ApiFeed._get_cache_id("applause",None,offset))
		memcache.delete(ApiFeed._get_cache_id("moper",None,offset))
		memcache.delete(ApiFeed._get_cache_id(None,None,offset))
		return
	
	@staticmethod
	def _get_cache_id(order,bbs_id,offset):
		if(not order):
			order="none"
		if(not bbs_id):
			bbs_id="none"
		return BbsConst.OBJECT_CACHE_HEADER+"_"+order+"_"+bbs_id+"_"+str(offset)
	
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
	def feed_get_thread_list(req):
		offset=0
		if(req.request.get("offset")):
			offset=int(req.request.get("offset"))

		cache_id=ApiFeed._get_cache_id(req.request.get("order"),req.request.get("bbs_id"),offset)

		cache_enable=0
		if(offset==0):
			cache_enable=1
		
		data=memcache.get(cache_id)
		if(data and cache_enable):
			return data

		query=ApiFeed._get_query(req.request.get("order"))

		bbs_id=None
		if(req.request.get("bbs_id")):
			query.filter("bbs_key =",db.get(MappingId.mapping(req.request.get("bbs_id"))))
			bbs_id=True

		limit=10
		if(req.request.get("limit")):
			limit=int(req.request.get("limit"))
		if(limit>100):
			limit=100
		
		thread_list=query.fetch(offset=offset,limit=limit)
		
		dic=ApiObject.create_thread_object_list(req,thread_list,bbs_id)

		if(cache_enable):
			memcache.set(cache_id,dic,60*10)
		
		return dic

#-------------------------------------------------------------------
#main
#-------------------------------------------------------------------

	def get(self):
		#日本語対応
		SetUtf8.set()
		if(ApiObject.check_api_capacity(self)):
			return
		
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
			dic=ApiFeed.feed_get_thread_list(self)

		ApiObject.write_json(self,dic)
		

