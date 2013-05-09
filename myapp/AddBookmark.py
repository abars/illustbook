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
import pickle
import time

import template_select

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
from myapp.AppCode import AppCode
from myapp.MesThread import MesThread
from myapp.MappingThreadId import MappingThreadId
from myapp.Alert import Alert
from myapp.SetUtf8 import SetUtf8
from myapp.RecentTag import RecentTag
from myapp.Bookmark import Bookmark
from myapp.StackFeed import StackFeed
from myapp.ApiObject import ApiObject
from myapp.ApiBookmark import ApiBookmark
from myapp.Ranking import Ranking
from myapp.BbsConst import BbsConst

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
	def add_comment(thread,user_id,comment):
		if(not comment):
			comment=""
		if(thread.bookmark_comment):
			dict=pickle.loads(thread.bookmark_comment)
		else:
			dict={}
		dict[user_id]=comment
		thread.bookmark_comment=db.Blob(pickle.dumps(dict))
		thread.put()

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
			Alert.alert_msg_with_write(self,"スレッドが見つかりません。");
			return
		
		#BBS取得
		bbs=AddBookmark.get_one_db(self.request.get("bbs_key"))
		if(not bbs and mode=="add_bbs"):
			Alert.alert_msg_with_write(self,"掲示板が見つかりません。");
			return
		
		#アプリ取得
		app=AddBookmark.get_one_db(self.request.get("app_key"))
		if(not app and mode=="add_app"):
			Alert.alert_msg_with_write(self,"アプリが見つかりません。");
			return
		
		#ログイン要求
		user = users.get_current_user()
		if(not(user)):
			Alert.alert_msg_with_write(self,"ブックマークをする場合はログインが必須です。");
			return
		
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user.user_id())
		if(bookmark==None):
			Alert.alert_msg_with_write(self,"ブックマークの取得に失敗しました。");
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

		comment=None
		if(self.request.get("comment")):
			comment=self.request.get("comment")

		#add bookmark
		feed_enable=False
		if(mode=="add"):
			feed_enable=AddBookmark.add_one(bookmark.thread_key_list,add_thread_key,thread)
			AddBookmark.add_comment(thread,user.user_id(),comment)
		if(mode=="add_bbs"):
			feed_enable=AddBookmark.add_one(bookmark.bbs_key_list,add_bbs_key,bbs)
		if(mode=="add_app"):
			AddBookmark.add_one(bookmark.app_key_list,add_app_key,app)
		if(mode=="add_user"):
			feed_enable=AddBookmark.add_user(bookmark.user_list,add_user_key)
		
		#del bookmark
		if(mode=="del"):
			AddBookmark.del_one(bookmark.thread_key_list,add_thread_key,thread)
		if(mode=="del_bbs"):
			AddBookmark.del_one(bookmark.bbs_key_list,add_bbs_key,bbs)
		if(mode=="del_app"):
			AddBookmark.del_one(bookmark.app_key_list,add_app_key,app)
		if(mode=="del_user"):
			bookmark.user_list.remove(add_user_key)

		#フォロー先のユーザのフォロワーを更新するようにリクエスト
		if(mode=="add_user" or mode=="del_user"):
			ApiObject.invalidate_follower_list(add_user_key)

		#write
		bookmark.put()

		#feed(feed内でもbookmark.putを行うため、bookmark.putの前に置いてはいけない)
		if(mode=="add"):
			if(feed_enable):
				StackFeed.feed_new_bookmark_thread(user,thread,comment)
				Ranking.add_rank_global(thread,BbsConst.SCORE_BOOKMARK)
		if(mode=="add_bbs"):
			if(feed_enable):
				StackFeed.feed_new_bookmark_bbs(user,bbs)
		if(mode=="add_user"):
			if(feed_enable):
				StackFeed.feed_new_follow(user,add_user_key)

		#redirect
		url="./mypage"
		if(mode=="del" or mode=="add"):
			url=url+"?tab=bookmark"
		if(mode=="del_bbs" or mode=="add_bbs"):
			url=url+"?tab=bbs"

		self.redirect(str(url))
		

