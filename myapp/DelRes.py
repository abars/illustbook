#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#Resの削除
#copyright 2010-2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

from google.appengine.ext import webapp

from google.appengine.ext.webapp import template
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
from myapp.Embedded import Embedded
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
from myapp.NicoTracker import NicoTracker
from myapp.UpdateProfile import UpdateProfile
from myapp.MyPage import MyPage
from myapp.ShowBookmark import ShowBookmark
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
from myapp.ChatConnected import ChatConnected
from myapp.ChatDisconnected import ChatDisconnected
from myapp.Ranking import Ranking
from myapp.ApiPacked import ApiPacked

webapp.template.register_template_library('templatetags.django_filter')

class DelRes(webapp.RequestHandler):
	def get(self):
		entry = db.get(self.request.get("entry_key"))
		
		if(self.request.get("res_key")=="all"):
			res=None
		else:
			res= db.get(self.request.get("res_key"))

		thread_key=entry.thread_key
		bbs_key=thread_key.bbs_key

		user = users.get_current_user()
		bbs_owner =not OwnerCheck.check(bbs_key,user)
		res_owner=False
		if(user and res and user.user_id()==res.user_id):
			res_owner=True
		
		if(not bbs_owner and not OwnerCheck.is_admin(user) and not res_owner):
			self.response.out.write(Alert.alert_msg("削除する権限がありません。",self.request.host))
			return

		if(not res):
			for res in entry.res_list:
				db.get(res).delete()
			entry.res_list=[]
		else:
			res.delete()
			idx = entry.res_list.index(db.Key(self.request.get("res_key")))
			entry.res_list.pop(idx)
		
		res_n=len(entry.res_list)
		if(res_n>=1):
			entry.date=db.get(entry.res_list[res_n-1]).date
		else:
			entry.date=entry.create_date

		entry.put()

		url=MappingThreadId.get_thread_url("./",bbs_key,thread_key)
		self.redirect(str(url))
		
		thread = db.get(str(thread_key.key()))
		thread.comment_cnt=thread.comment_cnt-1
		thread.put()

		RecentCommentCache.invalidate(bbs_key)

