#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#コメントの表示・非表示を切り替え
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
from myapp.NicoTracker import NicoTracker
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
from myapp.ChatConnected import ChatConnected
from myapp.ChatDisconnected import ChatDisconnected
from myapp.Ranking import Ranking
from myapp.ApiPacked import ApiPacked

import template_select

class VisibilityChangeEntry(webapp.RequestHandler):
	def get(self):
		bbs = db.get(self.request.get("bbs_key"))
		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			return
		entry = db.get(self.request.get("entry_key"))
		if(entry.hidden_flag):
			entry.hidden_flag = 0
		else:
			entry.hidden_flag = 1
		entry.put()

		thread = db.get(self.request.get("thread_key"))
		url=MappingThreadId.get_thread_url("./",bbs,thread)
		self.redirect(str(url))