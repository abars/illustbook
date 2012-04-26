#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#マイページに表示するフィードを作成
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

from google.appengine.ext.webapp import template
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
from myapp.ApiObject import ApiObject

from myapp.UTC import UTC
from myapp.JST import JST

class StackFeed(webapp.RequestHandler):
	#-----------------------------------------------
	#フィード1つをデータストアに格納する
	#-----------------------------------------------

	@staticmethod
	def _get_follow_list(user_id):
		if(user_id):
			query_follow=Bookmark.all().filter("user_list =",user_id)
			follow_list=query_follow.fetch(limit=100)
			return follow_list
		return None
	
	@staticmethod
	def _create_new_thread(user,bbs,thread):
		data=StackFeedData()
		data.feed_mode="bbs_new_illust"

		data.from_user_id=thread.user_id
		data.to_user_id=None

		data.user_key=None
		data.bbs_key=bbs
		data.thread_key=thread
		data.message=""
		data.create_date=datetime.datetime.today()
		data.put()
		return data

	@staticmethod
	def _create_new_bookmark_bbs(user_id,bbs):
		data=StackFeedData()
		data.feed_mode="new_bookmark_bbs"

		data.from_user_id=user_id
		data.to_user_id=None

		data.user_key=None
		data.bbs_key=bbs
		data.thread_key=None
		data.message=""
		data.create_date=datetime.datetime.today()
		data.put()
		return data
		
	@staticmethod
	def _create_new_bookmark_thread(user_id,thread):
		data=StackFeedData()
		data.feed_mode="new_bookmark_thread"

		data.from_user_id=user_id
		data.to_user_id=None

		data.user_key=None
		data.bbs_key=thread.bbs_key
		data.thread_key=thread
		data.message=""
		data.create_date=datetime.datetime.today()
		data.put()
		return data

	@staticmethod
	def _create_new_comment_thread(user_id,thread):
		data=StackFeedData()
		data.feed_mode="new_comment_thread"

		data.from_user_id=user_id
		data.to_user_id=None

		data.user_key=None
		data.bbs_key=thread.bbs_key
		data.thread_key=thread
		data.message=""
		data.create_date=datetime.datetime.today()
		data.put()
		return data
	
	@staticmethod
	def _create_new_follow(user_id,add_user_key):
		data=StackFeedData()
		data.feed_mode="new_follow"

		data.from_user_id=user_id
		data.to_user_id=None

		data.user_key=add_user_key
		data.bbs_key=None
		data.thread_key=None
		data.message=""
		data.create_date=datetime.datetime.today()
		data.put()
		return data
	
	@staticmethod
	def _append_one(data,user_id):
		if(not user_id):
			return
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user_id)
		if(bookmark):
			if(bookmark.user_id==data.from_user_id and data.feed_mode!="message"):
				return	#自分にはフィードしない
			if(not bookmark.stack_feed_list):
				bookmark.stack_feed_list=[]
			
			#重複判定
			if(bookmark.stack_feed_list.count(data.key())>=1):
				return
			
			bookmark.stack_feed_list.insert(0,data.key())
			if(bookmark.user_id!=data.from_user_id):
				if(not bookmark.new_feed_count):
					bookmark.new_feed_count=1
				else:
					bookmark.new_feed_count=bookmark.new_feed_count+1
			bookmark.put()
	
	#-----------------------------------------------
	#ユーザからフィード要求を受ける最上位
	#-----------------------------------------------
	
	#要求を受けたらTaskQueueに格納する
	
	@staticmethod
	def feed_new_thread(user,bbs,thread):
		user_id=""
		if(user):
			user_id=user.user_id()
		taskqueue.add(url="/stack_feed_worker",params={"mode":"bbs_new_illust","user_id":user_id,"bbs":str(bbs.key()),"thread":str(thread.key())},queue_name="feed")

	@staticmethod
	def feed_new_bookmark_bbs(user,bbs):
		user_id=user.user_id()
		taskqueue.add(url="/stack_feed_worker",params={"mode":"new_bookmark_bbs","user_id":user_id,"bbs":str(bbs.key())},queue_name="feed")

	@staticmethod
	def feed_new_bookmark_thread(user,thread):
		user_id=user.user_id()
		taskqueue.add(url="/stack_feed_worker",params={"mode":"new_bookmark_thread","user_id":user_id,"thread":str(thread.key())},queue_name="feed")

	@staticmethod
	def feed_new_comment_thread(user,thread):
		user_id=""
		if(user):
			user_id=user.user_id()
		taskqueue.add(url="/stack_feed_worker",params={"mode":"new_comment_thread","user_id":user_id,"thread":str(thread.key())},queue_name="feed")
	
	@staticmethod
	def feed_new_response_entry(user,thread,entry):
		user_id=""
		if(user):
			user_id=user.user_id()
		taskqueue.add(url="/stack_feed_worker",params={"mode":"new_response_entry","user_id":user_id,"thread":str(thread.key()),"entry":str(entry.key())},queue_name="feed")
	
	@staticmethod
	def feed_new_follow(user,add_user_key):
		user_id=user.user_id()
		taskqueue.add(url="/stack_feed_worker",params={"mode":"new_follow","user_id":user_id,"follow_user_id":add_user_key},queue_name="feed")
	
	@staticmethod
	def feed_new_message(user,data):
		data_key=str(data.key())
		user_id=user.user_id()
		taskqueue.add(url="/stack_feed_worker",params={"mode":"new_message","user_id":user_id,"data":data_key},queue_name="feed")

	#-----------------------------------------------
	#TaskQueueのWorker
	#-----------------------------------------------
	
	@staticmethod
	def _feed_to_follower(data,user_id):
		follow_list=StackFeed._get_follow_list(user_id)
		if(follow_list):
			for bookmark in follow_list:
				StackFeed._append_one(data,bookmark.user_id)	#重複は_append_oneで検出

	@staticmethod
	def _feed_new_thread_core(user_id,bbs,thread):
		#新規イラストが投稿された場合、
		#投稿先の掲示板をブックマークしているユーザと、
		#投稿ユーザをフォローしているユーザにフィード
		
		if(not bbs):
			return
		if(not thread):
			return
		
		query_bbs_bookmark=Bookmark.all().filter("bbs_key_list = ",db.Key(str(bbs.key())))
		bookmark_list=query_bbs_bookmark.fetch(limit=100)
		
		follow_list=StackFeed._get_follow_list(user_id)
		if(follow_list):
			bookmark_list=bookmark_list+follow_list
		
		data=StackFeed._create_new_thread(user_id,bbs,thread)

		for bookmark in bookmark_list:
			StackFeed._append_one(data,bookmark.user_id)
	
	@staticmethod
	def _feed_new_bookmark_bbs_core(user_id,bbs):
		#掲示板がブックマークされた場合、
		#掲示板のオーナーと、
		#ブックマークしたユーザをフォローしているユーザにフィード

		if(not bbs):
			return
	
		bbs_owner_user_id=bbs.user_id
		
		data=StackFeed._create_new_bookmark_bbs(user_id,bbs)
		StackFeed._append_one(data,bbs_owner_user_id)

		StackFeed._feed_to_follower(data,user_id)

	@staticmethod
	def _feed_new_bookmark_thread_core(user_id,thread):
		#イラストがブックマークされた場合、
		#イラストのオーナーと、
		#ブックマークしたユーザをフォローしているユーザにフィード
		
		if(not thread):
			return

		thread_owner_user_id=thread.user_id

		data=StackFeed._create_new_bookmark_thread(user_id,thread)
		StackFeed._append_one(data,thread_owner_user_id)

		StackFeed._feed_to_follower(data,user_id)

	@staticmethod
	def _feed_new_comment_thread_and_entry_core(user_id,thread,entry):
		#コメントが投稿された場合、
		#イラストのオーナーと、
		#その掲示板をブックマークしているユーザにフィード
		#返信が投稿された場合は、コメントの投稿者にもフィード
		
		if(not thread):
			return
		
		thread_owner_user_id=thread.user_id

		data=StackFeed._create_new_comment_thread(user_id,thread)
		StackFeed._append_one(data,thread_owner_user_id)
		
		if(entry):
			entry_owner_user_id=entry.user_id
			StackFeed._append_one(data,entry_owner_user_id)
		
		bbs=thread.bbs_key

		query_bbs_bookmark=Bookmark.all().filter("bbs_key_list = ",db.Key(str(bbs.key())))
		bookmark_list=query_bbs_bookmark.fetch(limit=100)

		for bookmark in bookmark_list:
			StackFeed._append_one(data,bookmark.user_id)

	@staticmethod
	def _feed_new_follow_core(user_id,add_user_key):
		#フォローした場合、フォローされたユーザと、
		#フォローしたユーザをフォローしているユーザに通知
	
		data=StackFeed._create_new_follow(user_id,add_user_key)
		StackFeed._append_one(data,add_user_key)

		StackFeed._feed_to_follower(data,user_id)
	
	@staticmethod
	def _feed_new_message_core(user_id,data):
		#宛先ユーザと、フォローしているユーザに通知
		
		#宛先ユーザへは投稿時に送ってしまう
		#if(data.to_user_id):
		#	StackFeed._append_one(data,data.to_user_id)

		StackFeed._feed_to_follower(data,user_id)
		
	def post(self):
		mode=self.request.get("mode")
		user_id=self.request.get("user_id")
		if(mode=="bbs_new_illust"):
			bbs=db.get(self.request.get("bbs"))
			thread=db.get(self.request.get("thread"))
			StackFeed._feed_new_thread_core(user_id,bbs,thread)
		if(mode=="new_bookmark_bbs"):
			bbs=db.get(self.request.get("bbs"))
			StackFeed._feed_new_bookmark_bbs_core(user_id,bbs)
		if(mode=="new_bookmark_thread"):
			thread=db.get(self.request.get("thread"))
			StackFeed._feed_new_bookmark_thread_core(user_id,thread)
		if(mode=="new_comment_thread"):
			thread=db.get(self.request.get("thread"))
			StackFeed._feed_new_comment_thread_and_entry_core(user_id,thread,None)
		if(mode=="new_response_entry"):
			thread=db.get(self.request.get("thread"))
			entry=db.get(self.request.get("entry"))
			StackFeed._feed_new_comment_thread_and_entry_core(user_id,thread,entry)
		if(mode=="new_follow"):
			add_user_key=self.request.get("follow_user_id")
			StackFeed._feed_new_follow_core(user_id,add_user_key)
		if(mode=="new_message"):
			data=db.get(self.request.get("data"))
			StackFeed._feed_new_message_core(user_id,data)

