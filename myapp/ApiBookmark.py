#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ブックマーク系の公開API
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

class ApiBookmark(webapp.RequestHandler):

#-------------------------------------------------------------------
#bookmark class
#-------------------------------------------------------------------

	@staticmethod
	def bookmark_get_thread_list(req,user_id):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			return []
		thread_key_list=bookmark.thread_key_list
		
		thread_key_list=ApiObject.offset_and_limit(req,thread_key_list)

		return ApiObject.create_thread_object_list(req,thread_key_list,"bookmark")

	@staticmethod
	def bookmark_get_bbs_list(req,user_id):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			return []
		dic=[]
		for bbs_key in bookmark.bbs_key_list:
			bbs=db.get(bbs_key)
			one_dic=ApiObject.create_bbs_object(req,bbs)
			dic.append(one_dic)
		return dic

	@staticmethod
	def bookmark_get_app_list(req,user_id):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			return []
		dic=[]
		for app_key in bookmark.app_key_list:
			app=db.get(app_key)
			one_dic=ApiObject.create_app_object(req,app)
			dic.append(one_dic)
		return dic
	
	@staticmethod
	def bookmark_get_bbs_user_list(req):
		bbs_key=req.request.get("bbs_key")
		bookmark_list=Bookmark.all().filter("bbs_key_list =",db.Key(bbs_key)).fetch(limit=100)
		dic=[]
		for bookmark in bookmark_list:
			one_dic=ApiObject.create_user_object(req,bookmark)
			dic.append(one_dic)
		return dic
	
	@staticmethod
	def bookmark_get_thread_user_list(req):
		thread_key=req.request.get("thread_key")
		bookmark_list=Bookmark.all().filter("thread_key_list =",db.Key(thread_key)).fetch(limit=100)
		dic=[]
		for bookmark in bookmark_list:
			one_dic=ApiObject.create_user_object(req,bookmark)
			dic.append(one_dic)
		return dic

	@staticmethod
	def bookmark_get_app_user_list(req):
		thread_key=req.request.get("app_key")
		bookmark_list=Bookmark.all().filter("app_key_list =",db.Key(thread_key)).fetch(limit=100)
		dic=[]
		for bookmark in bookmark_list:
			one_dic=ApiObject.create_user_object(req,bookmark)
			dic.append(one_dic)
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

		#ブックマーククラス
		if(method=="getThreadList"):
			dic=ApiBookmark.bookmark_get_thread_list(self,user_id)
		if(method=="getBbsList"):
			dic=ApiBookmark.bookmark_get_bbs_list(self,user_id)
		if(method=="getAppList"):
			dic=ApiBookmark.bookmark_get_app_list(self,user_id)
		if(method=="getBbsUserList"):
			dic=ApiBookmark.bookmark_get_bbs_user_list(self)
		if(method=="getThreadUserList"):
			dic=ApiBookmark.bookmark_get_thread_user_list(self)
		if(method=="getAppUserList"):
			dic=ApiBookmark.bookmark_get_app_user_list(self)
		
		if(dic==None):
			dic={"status":"failed","message":"ブックマークの取得に失敗しました。"}
			ApiObject.write_json_core(self,dic)
			return dic

		ApiObject.write_json(self,dic)
