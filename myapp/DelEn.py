#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#Entryの削除
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

import template_select

class DelEn(webapp.RequestHandler):
	def get(self):
		bbs = db.get(self.request.get("bbs_key"))
		user = users.get_current_user()
		entry = db.get(self.request.get("entry_key"))

		entry_owner=False
		if(user and user.user_id()==entry.user_id):
			entry_owner=True
		
		bbs_owner=not OwnerCheck.check(bbs,user)

		if(not bbs_owner and not OwnerCheck.is_admin(user) and not entry_owner):
			self.response.out.write(Alert.alert_msg("削除する権限がありません。",self.request.host))
			return
		entry.del_flag = 0
		entry.put()

		thread = db.get(self.request.get("thread_key"))
		thread.comment_cnt=thread.comment_cnt-1
		thread.cached_entry_key=[]
		thread.cached_entry_key_enable=None
		thread.put()

		url=MappingThreadId.get_thread_url("./",bbs,thread)+"?comment_edit=1"
		self.redirect(str(url))

		RecentCommentCache.invalidate(bbs)

