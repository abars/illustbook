#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザ系の公開API
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

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

from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.MesThread import MesThread
from myapp.MappingId import MappingId
from myapp.Bbs import Bbs
from myapp.BbsConst import BbsConst
from myapp.Bookmark import Bookmark
from myapp.AddBookmark import AddBookmark
from myapp.ApiObject import ApiObject

class ApiUser(webapp.RequestHandler):

#-------------------------------------------------------------------
#user class
#-------------------------------------------------------------------

	@staticmethod
	def user_get_profile(req,user_id):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(not bookmark):
			return []
		one_dic=ApiObject.create_user_object(req,bookmark)
		one_dic["profile"]=bookmark.profile
		return one_dic
	
	@staticmethod
	def user_get_follow(req,user_id):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(not bookmark):
			return []
		
		bookmark_list=ApiObject.get_bookmark_list(bookmark.user_list)
		
		dic=[]
		for one_user in bookmark.user_list:
			bookmark=bookmark_list[one_user]
			#bookmark=ApiObject.get_bookmark_of_user_id(one_user)
			if(bookmark):
				one_dic=ApiObject.create_user_object(req,bookmark)
				dic.append(one_dic)
		return dic
	
	@staticmethod
	def user_get_follower(req,user_id):
		follower=None
		try:
			query=Bookmark.all().filter("user_list =",user_id)
			follower=query.fetch(limit=1000)
		except:
			return []
		dic=[]
		for bookmark in follower:
			one_dic=ApiObject.create_user_object(req,bookmark)
			dic.append(one_dic)
		return dic
	
	@staticmethod
	def user_get_user(req,user_id):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(not bookmark):
			return []
		return ApiObject.create_user_object(req,bookmark)
	
	@staticmethod
	def user_get_bbs_list(req,user_id):
		query=db.Query(Bbs,keys_only=True)
		query=query.filter("user_id =",user_id).order("-create_date")
		bbs_key_list=query.fetch(limit=1000,offset=0)
		dic=[]
		bbs_list=ApiObject.get_cached_object_list(bbs_key_list)
		for bbs in bbs_list:
			if(bbs.del_flag):
				continue
			one_dic=ApiObject.create_bbs_object(req,bbs)
			dic.append(one_dic)
		return dic;

	@staticmethod
	def user_get_thread_list(req,user_id):
		query=db.Query(MesThread)

		query=query.filter("illust_mode IN",[BbsConst.ILLUSTMODE_ILLUST,BbsConst.ILLUSTMODE_MOPER])
		query=query.filter("user_id =",user_id).order("-create_date")

		offset=0
		if(req.request.get("offset")):
			offset=int(req.request.get("offset"))
		
		limit=10
		if(req.request.get("limit")):
			limit=int(req.request.get("limit"))

		thread_key_list=[]
		thread_list=query.fetch(limit=limit,offset=offset)
		for thread in thread_list:
			thread_key_list.append(str(thread.key()))
		
		return ApiObject.create_thread_object_list(req,thread_key_list,"user")

	@staticmethod
	def user_get_timeline(req,user_id):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			return []

		feed_list=ApiObject.offset_and_limit(req,bookmark.stack_feed_list)
		
		feed_list=ApiObject.get_cached_object_list(feed_list)
		
		dic=ApiObject.create_feed_object_list(req,feed_list)
		return dic
		
#-------------------------------------------------------------------
#main
#-------------------------------------------------------------------

	def get(self):
		SetUtf8.set()
		if(ApiObject.check_api_capacity(self)):
			return
		dic=ApiUser.get_core(self)
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

		#ユーザクラス
		if(method=="getUser"):
			dic=ApiUser.user_get_user(self,user_id)
		if(method=="getProfile"):
			dic=ApiUser.user_get_profile(self,user_id)
		if(method=="getFollow"):
			dic=ApiUser.user_get_follow(self,user_id)
		if(method=="getFollower"):
			dic=ApiUser.user_get_follower(self,user_id)
		if(method=="getBbsList"):
			dic=ApiUser.user_get_bbs_list(self,user_id)
		if(method=="getThreadList"):
			dic=ApiUser.user_get_thread_list(self,user_id)
		if(method=="getTimeline"):
			dic=ApiUser.user_get_timeline(self,user_id)
			
		return ApiObject.add_json_success_header(dic)
