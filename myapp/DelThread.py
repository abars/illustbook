#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#Threadの削除
#copyright 2010-2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

from google.appengine.ext import webapp

import template_select
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Analyze import Analyze
from myapp.Bbs import Bbs
from myapp.Entry import Entry
from myapp.Counter import Counter
from myapp.Response import Response
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.ThreadImage import ThreadImage
from myapp.SetUtf8 import SetUtf8
from myapp.RecentCommentCache import RecentCommentCache
from myapp.MappingId import MappingId
from myapp.SpamCheck import SpamCheck
from myapp.SpamDelete import SpamDelete
from myapp.AddNewThread import AddNewThread
from myapp.Alert import Alert
from myapp.OwnerCheck import OwnerCheck
from myapp.UpdateBbs import UpdateBbs
from myapp.AddEntry import AddEntry
from myapp.PageGenerate import PageGenerate
from myapp.Applause import Applause
from myapp.RssFeed import RssFeed
from myapp.ShowThread import ShowThread
from myapp.ShowBbs import ShowBbs
from myapp.MoveAccount import MoveAccount
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.AnalyzeAccess import AnalyzeAccess
from myapp.CssDesign import CssDesign
from myapp.ImageFile import ImageFile
from myapp.AddRes import AddRes
from myapp.UpdateThread import UpdateThread
from myapp.EditThread import EditThread
from myapp.ViolationTerms import ViolationTerms
from myapp.MappingThreadId import MappingThreadId
from myapp.DrawWindow import DrawWindow
from myapp.AddTag import AddTag
from myapp.SearchTag import SearchTag
from myapp.Bookmark import Bookmark
from myapp.AddBookmark import AddBookmark
from myapp.UpdateProfile import UpdateProfile
from myapp.MyPage import MyPage
from myapp.Comic import Comic
from myapp.AppPortal import AppPortal
from myapp.ApiUser import ApiUser
from myapp.ApiBookmark import ApiBookmark
from myapp.ApiFeed import ApiFeed
from myapp.ApiJs import ApiJs
from myapp.DevPortal import DevPortal
from myapp.SchemeUpdate import SchemeUpdate
from myapp.ApiPerpetuation import ApiPerpetuation
from myapp.EditBbs import EditBbs
from myapp.AppImage import AppImage
from myapp.SiteAnalyzer import SiteAnalyzer
from myapp.StackFeed import StackFeed
from myapp.StackFeedTweet import StackFeedTweet
from myapp.ApiObject import ApiObject
from myapp.CounterWorker import CounterWorker
from myapp.ShowIcon import ShowIcon
from myapp.CheckId import CheckId
from myapp.Ranking import Ranking
from myapp.ApiPacked import ApiPacked
from myapp.ApiUser import ApiUser

import template_select

class DelThread(webapp.RequestHandler):
	@staticmethod
	def delete_thread_core(thread):
		#イラストの総数の更新リクエスト
		thread.bbs_key.cached_threads_num=None
		thread.bbs_key.put()
		if(thread.user_id):
			ApiUser.invalidate_thread_count(thread.user_id)

		#レスの削除
		entry_query=Entry.all().filter("thread_key =",thread)
		for entry in entry_query:
			if(entry.illust_reply_image_key):
				entry.illust_reply_image_key.delete()

		#画像の削除
		if(thread.image_key):
			if(thread.image_key.chunk_list_key):
				for key in thread.image_key.chunk_list_key:
					db.get(key).delete()
			thread.image_key.delete()

		thread.delete()

	def get(self):
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			bbs=None
		try:
			thread = db.get(self.request.get("thread_key"))
		except:
			thread=None
		
		if(not bbs or not thread):
			self.response.out.write(Alert.alert_msg("削除対象が見つかりません。",self.request.host))
			return

		is_english=CssDesign.is_english(self)
		
		del_ok=0		
		if(self.request.get("del_key")):
			if(thread.delete_key):
				if(thread.delete_key==self.request.get("del_key")):
					del_ok=1
				else:
					msg="削除キーが一致しません。"
					if(is_english):
						msg="invalid key"
					self.response.out.write(Alert.alert_msg(msg,self.request.host))
					return;
		
		user = users.get_current_user()

		bbs_owner = not OwnerCheck.check(bbs,user)
		thread_owner=False
		if(user and user.user_id()==thread.user_id):
			thread_owner=True
		
		if(del_ok==0):
			if(not bbs_owner and not thread_owner and not OwnerCheck.is_admin(user)):
				self.response.out.write(Alert.alert_msg("削除権限がありません。",self.request.host))
				return

		DelThread.delete_thread_core(thread)

		bbs.cached_thumbnail_key=None
		bbs.put()

		ApiFeed.invalidate_cache()

		url=MappingId.get_usr_url("./",bbs)
		self.redirect(str(url))

