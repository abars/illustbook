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
import logging
import pickle

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

import template_select

from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.MesThread import MesThread
from myapp.MappingId import MappingId
from myapp.Bbs import Bbs
from myapp.BbsConst import BbsConst
from myapp.Bookmark import Bookmark
from myapp.ApiObject import ApiObject

class ApiBookmark(webapp.RequestHandler):

#-------------------------------------------------------------------
#bookmark class
#-------------------------------------------------------------------

	@staticmethod
	def add_removed_thread_to_dic(req,dic,thread_key_list):
		if len(dic)==len(thread_key_list):
			return
		
		#削除されたスレッドも一覧に表示する
		appear={}
		for thread in dic:
			appear[thread["key"]]=True
		for key in thread_key_list:
			key=str(key)
			if key not in appear:
				removed_url="";
				removed_thread={
					"title":"",
					"author":"",
					"summary":"イラストは削除されました",
					"thumbnail_url":removed_url,
					"image_url":removed_url,
					"create_date":"",
					"thread_url":"",
					"applause":0,
					"bookmark":0,
					"key":str(key),
					"disable_news":0}
				dic.append(removed_thread)

	@staticmethod
	def add_removed_bbs_to_dic(req,dic,bbs_key_list):
		if len(dic)==len(bbs_key_list):
			return

		#削除された掲示板も一覧に表示する
		appear={}
		for bbs in dic:
			appear[bbs["key"]]=True
		for key in bbs_key_list:
			key=str(key)
			if key not in appear:
				removed_url="";
				removed_bbs={
					"title":"掲示板は削除されました",
					"author":"",
					"thumbnail_url":removed_url,
					"create_date":"",
					"bookmark":0,
					"key":str(key)}
				dic.append(removed_bbs)

	@staticmethod
	def bookmark_get_thread_list(req,user_id,bookmark=None):
		if(not bookmark):
			bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			return []

		thread_key_list=bookmark.thread_key_list
		thread_key_list=ApiObject.offset_and_limit(req,thread_key_list)

		dic=ApiObject.create_thread_object_list(req,thread_key_list,"bookmark")
		ApiBookmark.add_removed_thread_to_dic(req,dic,thread_key_list)

		return dic

	@staticmethod
	def bookmark_get_is_bookmark_thread_exist(req,user_id,bookmark=None):
		if(not bookmark):
			bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			return 0
		return len(bookmark.thread_key_list)

	@staticmethod
	def bookmark_get_bbs_list(req,user_id):
		return ApiBookmark._bookmark_get_bbs_list_core(req,user_id,False)

	@staticmethod
	def bookmark_get_mute_bbs_list(req,user_id):
		return ApiBookmark._bookmark_get_bbs_list_core(req,user_id,True)

	@staticmethod
	def _bookmark_get_bbs_list_core(req,user_id,mute):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			return []
		dic=[]
		if(mute):
			bbs_key_list=bookmark.get_mute_bbs_list()
		else:
			bbs_key_list=bookmark.bbs_key_list
		bbs_list=ApiObject.get_cached_object_list(bbs_key_list)
		for bbs in bbs_list:
			one_dic=ApiObject.create_bbs_object(req,bbs)
			if(one_dic):
				dic.append(one_dic)
		
		ApiBookmark.add_removed_bbs_to_dic(req,dic,bbs_key_list)

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
		
		#comment
		comment={}
		thread=ApiObject.get_cached_object(db.Key(thread_key))
		if(not thread):
			return []
		if(thread.bookmark_comment):
			comment=pickle.loads(thread.bookmark_comment)

		#user list
		dic=[]
		for bookmark in bookmark_list:
			one_dic=ApiObject.create_user_object(req,bookmark)
			user_id=None
			if(one_dic.has_key("user_id")):
				user_id=one_dic["user_id"]
			if(user_id and comment.has_key(user_id)):
				one_dic["comment"]=comment[user_id]
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
		dic=ApiBookmark.get_core(self)
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
		else:
			dic=ApiObject.add_json_success_header(dic)
		
		return dic
