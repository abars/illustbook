#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ブックマークに追加する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from Bbs import Bbs
from MesThread import MesThread
from AppCode import AppCode
from MesThread import MesThread
from MappingThreadId import MappingThreadId
from Alert import Alert
from SetUtf8 import SetUtf8
from RecentTag import RecentTag
from Bookmark import Bookmark
from StackFeed import StackFeed
from ApiObject import ApiObject

class AddBookmark(webapp.RequestHandler):
	@staticmethod
	def get_bookmark_count(thread,add_thread_key):
		#現在のブックマーク数を取得
		if(type(thread)==MesThread):
			return Bookmark.all().filter("thread_key_list =",add_thread_key).count()
		if(type(thread)==Bbs):
			return Bookmark.all().filter("bbs_key_list =",add_thread_key).count()
		if(type(thread)==AppCode):
			return Bookmark.all().filter("app_key_list =",add_thread_key).count()
		return 0

	@staticmethod
	def add_one(thread_key_list,add_thread_key,thread):
		if(thread_key_list.count(add_thread_key)==0):
			#ブックマークに追加
			thread_key_list.insert(0,add_thread_key)

			#格納
			thread.bookmark_count=AddBookmark.get_bookmark_count(thread,add_thread_key)+1
			thread.put()
			return True
		else:
			#ブックマークをソート
			thread_key_list.remove(add_thread_key)
			thread_key_list.insert(0,add_thread_key)

			#現在のブックマーク数で更新
			thread.bookmark_count=AddBookmark.get_bookmark_count(thread,add_thread_key)
			thread.put()
			
			return False
	
	@staticmethod
	def del_one(thread_key_list,add_thread_key,thread):
		if(thread_key_list.count(add_thread_key)>=1):
			thread_key_list.remove(add_thread_key)
			if(thread):
				thread.bookmark_count=AddBookmark.get_bookmark_count(thread,add_thread_key)-1
				thread.put()

	@staticmethod
	def add_user(user_list,add_user_key):
		if(user_list.count(add_user_key)==0):
			user_list.insert(0,add_user_key)
			return True
		else:
			user_list.remove(add_user_key)
			user_list.insert(0,add_user_key)
			return False
		
	@staticmethod
	def get_one_db(key):
		thread=None
		try:
			thread = db.get(key)
		except:
			thread=None
		return thread

	def get(self):
		SetUtf8.set()

		mode = self.request.get("mode")

		#スレッド取得
		thread = AddBookmark.get_one_db(self.request.get("thread_key"))
		if(not thread and mode=="add"):	#削除はスレッドが見つからなくてもできるようにする
			self.response.out.write(Alert.alert_msg("スレッドが見つかりません。",self.request.host));
			return
		
		#BBS取得
		bbs=AddBookmark.get_one_db(self.request.get("bbs_key"))
		if(not bbs and mode=="add_bbs"):
			self.response.out.write(Alert.alert_msg("掲示板が見つかりません。",self.request.host));
			return
		
		#アプリ取得
		app=AddBookmark.get_one_db(self.request.get("app_key"))
		if(not app and mode=="add_app"):
			self.response.out.write(Alert.alert_msg("アプリが見つかりません。",self.request.host));
			return
		
		#ログイン要求
		user = users.get_current_user()
		if(not(user)):
			self.response.out.write(Alert.alert_msg("ブックマークをする場合はログインが必須です。",self.request.host));
			return
		
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user.user_id())
		if(bookmark==None):
			self.response.out.write(Alert.alert_msg("ブックマークの取得に失敗しました。",self.request.host));
			return
		
		#ユーザ
		add_user_key=self.request.get("user_key")

		#ブックマーク数を初期化
		if(thread):
			if(not thread.bookmark_count):
				thread.bookmark_count=0
		if(bbs):
			if(not bbs.bookmark_count):
				bbs.bookmark_count=0

		add_thread_key=None
		if(self.request.get("thread_key")):
			add_thread_key=db.Key(self.request.get("thread_key"))
		
		add_bbs_key=None
		if(self.request.get("bbs_key")):
			add_bbs_key=db.Key(self.request.get("bbs_key"))
		
		add_app_key=None
		if(self.request.get("app_key")):
			add_app_key=db.Key(self.request.get("app_key"))

		if(mode=="add"):
			if(AddBookmark.add_one(bookmark.thread_key_list,add_thread_key,thread)):
				StackFeed.feed_new_bookmark_thread(user,thread)
		if(mode=="add_bbs"):
			if(AddBookmark.add_one(bookmark.bbs_key_list,add_bbs_key,bbs)):
				StackFeed.feed_new_bookmark_bbs(user,bbs)
		if(mode=="add_app"):
			AddBookmark.add_one(bookmark.app_key_list,add_app_key,app)
		if(mode=="add_user"):
			if(AddBookmark.add_user(bookmark.user_list,add_user_key)):
				StackFeed.feed_new_follow(user,add_user_key)
			
		if(mode=="del"):
			AddBookmark.del_one(bookmark.thread_key_list,add_thread_key,thread)
		if(mode=="del_bbs"):
			AddBookmark.del_one(bookmark.bbs_key_list,add_bbs_key,bbs)
		if(mode=="del_app"):
			AddBookmark.del_one(bookmark.app_key_list,add_app_key,app)
		if(mode=="del_user"):
			bookmark.user_list.remove(add_user_key)

		bookmark.put()
		
		self.redirect(str("./mypage"))
		

