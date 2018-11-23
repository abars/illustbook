#!-*- coding:utf-8 -*-
#!/usr/bin/env python

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
from myapp.Admin import Admin
from myapp.AddNewBbs import AddNewBbs
from myapp.PageGenerate import PageGenerate
from myapp.Applause import Applause
from myapp.RssFeed import RssFeed
from myapp.ShowThread import ShowThread
from myapp.ShowBbs import ShowBbs
from myapp.MoveAccount import MoveAccount
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.MoperUpload import MoperUpload
from myapp.MoperImportRaster import MoperImportRaster
from myapp.MoperGuide import MoperGuide
from myapp.MoperLoad import MoperLoad
from myapp.MoperPlayer import MoperPlayer
from myapp.MoperDraw import MoperDraw
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
from myapp.Chat import Chat
from myapp.ChatConnected import ChatConnected
from myapp.ChatDisconnected import ChatDisconnected
from myapp.Ranking import Ranking
from myapp.ApiPacked import ApiPacked
from myapp.Pinterest import Pinterest
from myapp.DelThread import DelThread
from myapp.DelBbs import DelBbs
from myapp.DelEn import DelEn
from myapp.DelRes import DelRes
from myapp.RedirectBbs import RedirectBbs
from myapp.RedirectThread import RedirectThread
from myapp.VisibilityChangeEntry import VisibilityChangeEntry
from myapp.EditThreadList import EditThreadList
from myapp.SearchTag import SearchTag
from myapp.UploadTemp import UploadTemp
from myapp.AnalyticsGet import AnalyticsGet
from myapp.EventList import EventList

class RankingPortal(webapp.RequestHandler):
	def get(self):
		is_iphone=CssDesign.is_iphone(self)

		page=1
		page_unit=20
		if(self.request.get("page")):
			page=int(self.request.get("page"))
		
		rank=Ranking.get_or_insert(BbsConst.THREAD_RANKING_KEY_NAME)
		ranking_mode=self.request.get("mode")
		
		ranking_id_list=rank.user_id_ranking_list[(page-1)*page_unit:page*page_unit]
		ranking_list=[]
		for user_id in ranking_id_list:
			obj=ApiObject.get_bookmark_of_user_id(user_id)
			if(obj):
				if(obj.disable_rankwatch):
					ranking_list.append(None)
					continue
				obj=ApiObject.create_user_object(self,obj)
				ranking_list.append(obj)

		user = users.get_current_user()
		user_rank=0
		if(user):
			rank=Ranking.get_by_key_name(BbsConst.THREAD_RANKING_KEY_NAME)
			if(rank):
				user_rank=rank.get_user_rank(user.user_id())

		template_values = {
			'host': "./",
			'is_iphone': is_iphone,
			'user': user,
			'user_rank': user_rank,
			'redirect_url': self.request.path,
			'mode': "ranking",
			'header_enable': False,
			'ranking_list': ranking_list,
			'ranking_mode': ranking_mode,
			'page': page,
			'page_unit': page_unit
		}

		path = '/html/portal.html'
		self.response.out.write(template_select.render(path, template_values))
