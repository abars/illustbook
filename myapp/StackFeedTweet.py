#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#マイページのフィードにツイートする
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

from google.appengine.api.labs import taskqueue

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Entry import Entry
from myapp.Response import Response
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.ThreadImage import ThreadImage
from myapp.SpamCheck import SpamCheck
from myapp.Alert import Alert
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.ImageFile import ImageFile
from myapp.MappingThreadId import MappingThreadId
from myapp.Bookmark import Bookmark
from myapp.StackFeedData import StackFeedData
from myapp.StackFeed import StackFeed
from myapp.ApiObject import ApiObject
from myapp.MappingId import MappingId

from myapp.UTC import UTC
from myapp.JST import JST

class StackFeedTweet(webapp.RequestHandler):
	#def del_message(self,user):
	#	data=db.get(self.request.get("key"))
	#	if(data==None):
	#		self.response.out.write(Alert.alert_msg("ツイートが見つかりません。",self.request.host));
	#		return False
	#	if(data.from_user_id==user.user_id()):
	#		data.delete()
	#	else:
	#		self.response.out.write(Alert.alert_msg("認証に失敗しました。",self.request.host));
	#		return False
	#	return True

	def del_from_bookmark(self,bookmark,tweet):
		if(db.Key(tweet) in bookmark.stack_feed_list):
			bookmark.stack_feed_list.remove(db.Key(tweet))
		if(db.Key(tweet) in bookmark.my_timeline):
			bookmark.my_timeline.remove(db.Key(tweet))
		
	def del_message_list(self,user):
		if(self.request.get("user_id")!=user.user_id()):
			self.response.out.write(Alert.alert_msg("認証に失敗しました。",self.request.host));
			return False

		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user.user_id())
		if(bookmark==None):
			self.response.out.write(Alert.alert_msg("ユーザデータが見つかりません。",self.request.host));
			return False

		tweet_list=self.request.get_all("tweet_list")

		if(not tweet_list or len(tweet_list)==0):
			self.response.out.write(Alert.alert_msg("削除するツイートが選択されていません。",self.request.host));
			return False			

		for tweet in tweet_list:
			self.del_from_bookmark(bookmark,tweet)

			try:
				data=db.get(tweet)
			except:
				data=None
			if(data):
				if(data.from_user_id==user.user_id()):
					data.delete()

		bookmark.put()
		return True

	def del_message_all(self,user):
		if(self.request.get("user_id")!=user.user_id()):
			self.response.out.write(Alert.alert_msg("認証に失敗しました。",self.request.host));
			return False

		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user.user_id())
		if(bookmark==None):
			self.response.out.write(Alert.alert_msg("ユーザデータが見つかりません。",self.request.host));
			return False

		tweeet_list=StackFeedData.all().filter("from_user_id =",user.user_id()).filter("feed_mode =","message").fetch(limit=1000)

		delete_limit=100

		del_cnt=0
		for tweet in tweeet_list:
			if(tweet.from_user_id==user.user_id()):
				self.del_from_bookmark(bookmark,str(tweet.key()))
				tweet.delete()
				del_cnt=del_cnt+1
				if(del_cnt>=delete_limit):
					break

		if(del_cnt>=delete_limit):#len(bookmark.my_timeline)>=1):
			self.response.out.write(Alert.alert_msg(str(del_cnt)+"件のツイートを削除しましたが、ツイートを削除しきることができませんでした。リロードして下さい。",self.request.host));
			return False
		if(del_cnt==0):
			self.response.out.write(Alert.alert_msg("削除するツイートが見つかりませんでした。",self.request.host));
			return False

		#bookmark.stack_feed_list=[]
		#bookmark.my_timeline=[]
		bookmark.put()

		self.response.out.write(Alert.alert_msg(str(del_cnt)+"件のツイートを削除しました。",self.request.host));
		return False

		#return True

	#def del_feed(self,user):
	#	bookmark=ApiObject.get_bookmark_of_user_id_for_write(user.user_id())
	#	if(bookmark==None):
	#		self.response.out.write(Alert.alert_msg("フィードリストが見つかりません。",self.request.host));
	#		return False

	#	failed_cnt=0

	#	try:
	#		bookmark.stack_feed_list.remove(db.Key(self.request.get("key")))
	#	except:
	#		failed_cnt=failed_cnt+1

	#	try:
	#		bookmark.my_timeline.remove(db.Key(self.request.get("key")))
	#	except:
	#		failed_cnt=failed_cnt+1

	#	if(failed_cnt==2):
	#		self.response.out.write(Alert.alert_msg("既に削除されています。",self.request.host));
	#		return False

	#	bookmark.put()
	#	return True
	
	#def retweet(self,user):
	#	data=db.get(self.request.get("key"))
		#comment=self.request.get("comment")
		
		#自分と相手にフィード
	#	StackFeed._append_one(data,user.user_id())
	#	if(data.to_user_id):
	#		StackFeed._append_one(data,data.to_user_id)
		
		#フォロワーにフィード
	#	StackFeed.feed_new_message(user,data)

	#	return True

	def add_new_message(self,user):
		#メッセージ作成
		data=StackFeedData()
		data.feed_mode="message"
		data.from_user_id=user.user_id()
		if(self.request.get("to_user_id")):
			data.to_user_id=self.request.get("to_user_id")
		else:
			data.to_user_id=None
		data.user_key=None
		data.bbs_key=None
		data.thread_key=None
		data.message=self.request.get("message")
		if(data.message==""):
			self.response.out.write(Alert.alert_msg("書き込みメッセージが存在しません。",self.request.host));
			return False
		data.create_date=datetime.datetime.today()

		#二重投稿防止
		message=memcache.get("StackFeedTweet")
		if(message==self.request.get("message")):
			self.response.out.write(Alert.alert_msg("このメッセージは既に投稿されています。",self.request.host));
			return False
		memcache.set("StackFeedTweet",self.request.get("message"),5)

		#保存
		data.put()
		
		#自分と相手にフィード
		StackFeed._append_one(data,user.user_id())
		if(data.to_user_id):
			StackFeed._append_one(data,data.to_user_id)
		
		#フォロワーにフィード
		StackFeed.feed_new_message(user,data)
		
		return True

	def redirect_main(self):
		#リダイレクト
		host="http://"+MappingId.mapping_host(self.request.host)+"/";
		redirect_url=host+"mypage?";

		#リダイレクト先は必ず自分とする（他人のタイムラインには投稿は表示されないので）
		#if(self.request.get("to_user_id")):
		#	redirect_url=redirect_url+"&user_id="+self.request.get("to_user_id")

		if(self.request.get("feed_page")):
			redirect_url=redirect_url+"&feed_page="+self.request.get("feed_page")
		if(self.request.get("tab")):
			redirect_url=redirect_url+"&tab="+self.request.get("tab")
		else:
			redirect_url=redirect_url+"&tab=feed"
		if(self.request.get("edit")):
			redirect_url=redirect_url+"&edit="+self.request.get("edit")

		self.redirect(str(redirect_url))

	def get(self):
		user = users.get_current_user()
		if(not user):
			self.response.out.write(Alert.alert_msg("ログインが必要です。",self.request.host));
			return
		#if(self.request.get("mode")=="del_tweet_all"):
		#	if(self.del_message_all(user)):
		#		self.redirect_main()
		#if(self.request.get("mode")=="del_tweet"):
		#	if(self.del_message(user)):
		#		self.redirect_main()
		#if(self.request.get("mode")=="del_feed"):
		#	if(self.del_feed(user)):
		#		self.redirect_main()
		#if(self.request.get("mode")=="retweet"):
		#	if(self.retweet(user)):
		#		self.redirect_main()
		
	def post(self):
		user = users.get_current_user()
		if(self.request.get("mode")=="add"):
			if(self.add_new_message(user)):
				self.redirect_main()
		if(self.request.get("mode")=="del_tweet_list"):
			if(self.del_message_list(user)):
				self.redirect_main()
		if(self.request.get("mode")=="del_tweet_all"):
			if(self.del_message_all(user)):
				self.redirect_main()
		