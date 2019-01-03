#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#メイン関数とポータル関係
#copyright 2010-2012 ABARS all rights reserved.
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

#-----------------------------------------------------------------
#DB
#-----------------------------------------------------------------

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
from myapp.RankingPortal import RankingPortal
from myapp.SpamCheck import SpamCheck

#-----------------------------------------------------------------
#ポータル
#-----------------------------------------------------------------

class MainPage(webapp.RequestHandler):
	def get(self):
		#移動
		if(self.request.host=="illust-book.appspot.com"):
			self.redirect(str("http://www.illustbook.net/"))
			return
	
		SetUtf8.set()

		#ホストチェック
		if SpamCheck.is_deny(self.request):
			self.response.set_status(401)
			return
		
		#メンテナンス画面
		is_maintenance=0
		if(MaintenanceCheck.is_appengine_maintenance()):
			is_maintenance=1
		
		#BBS COUNT
		cache=SiteAnalyzer.get_cache()
		bbs_n=cache["bbs_n"]
		illust_n=cache["illust_n"]
		
		#最近のタグ
		tag_list=SearchTag.get_recent_tag("search_tag")
		
		#デベロッパーオプション
		user = users.get_current_user()
		is_dev_enable=OwnerCheck.is_admin(user)

		#iPhoneモードかどうか
		is_iphone=CssDesign.is_iphone(self)

		#リダイレクト
		if(BbsConst.PINTEREST_MODE):
			if((user and OwnerCheck.is_admin(user)) or BbsConst.PINTEREST_MODE==2):
				return Pinterest.get_core(self,Pinterest.PAGE_MODE_NORMAL)

		#URL生成
		template_values = {
			'host': "./",
			'mes_bord_url': 'mes_bord',
			'new_url': 'create_new_thread',
			'bbs_n':bbs_n,
			'illust_n':illust_n,
			'tag_list':tag_list,
			'is_dev_enable':is_dev_enable,
			'is_maintenance': is_maintenance,
			'is_iphone': is_iphone,
			'user': user,
			'redirect_url': self.request.path,
			'top_page': True,
			'mode': "index"
		}

		path = '/html/index.html'
		self.response.out.write(template_select.render(path, template_values))

class Portal(webapp.RequestHandler):
	@staticmethod
	def get(req,mode,header_enable):
		is_iphone=CssDesign.is_iphone(req)

		template_values = {
			'host': "./",
			'is_iphone': is_iphone,
			'user': users.get_current_user(),
			'redirect_url': req.request.path,
			'mode': mode,
			'header_enable': header_enable
		}

		path = '/html/portal.html'
		req.response.out.write(template_select.render(path, template_values))

class Terms(webapp.RequestHandler):
	def get(self):
		Portal.get(self,"terms",False)

class GuidePage(webapp.RequestHandler):
	def get(self):
		user=users.get_current_user()
		if(BbsConst.PINTEREST_MODE):
			if((user and OwnerCheck.is_admin(user)) or BbsConst.PINTEREST_MODE==2):
				Pinterest.get_core(self,Pinterest.PAGE_MODE_GUIDE)
				return
		Portal.get(self,"guide",True)

class ShowBookmark(webapp.RequestHandler):
	def get(self):
		return Pinterest.get_core(self,Pinterest.PAGE_MODE_BOOKMARK)

#-----------------------------------------------------------------
#振り分け
#-----------------------------------------------------------------

application = webapp.WSGIApplication(
	[('/', MainPage),
	('/pinterest', Pinterest),
	(r'/usr/(.*)/(.*)\.html',ShowThread),
	(r'/usr/(.*)/',ShowBbs),
	(r'/usr/(.*)/index.xml',RssFeed),
	(r'/(.*)/(.*)\.html',ShowThread),
	(r'/(.*)/',ShowBbs),
	(r'/(.*)/index.xml',RssFeed),
	('/guide', GuidePage),
	('/bbs_index', RedirectBbs),
	(r'/css/(.*)\.(css)',CssDesign), 
	(r'/css/(.*)\.(key)',CssDesign), 
	(r'/(img)/(.*)\.(jpg)',ImageFile), 
	(r'/(img)/(.*)\.(png)',ImageFile), 
	(r'/(img)/(.*)\.(txt)',ImageFile), 
	('/(thumbnail)/([^\.]*)\.(jpg)', ImageFile),
	('/(thumbnail)/([^\.]*)\.(gif)', ImageFile),
	('/(thumbnail)/([^\.]*)\.(png)', ImageFile),
	('/(thumbnail2)/([^\.]*)\.(jpg)', ImageFile),
	(r'/(tile)/(.*)\.(png)',ImageFile), 
	('/add_thread', AddNewThread),
	('/add_bbs', AddNewBbs),
	('/show_thread', RedirectThread),
	('/add_entry', AddEntry),
	('/del_ent', DelEn),
	('/vis_ent', VisibilityChangeEntry),
	('/del_bbs', DelBbs),
	('/upl_all', AddNewThread),
	('/upl_temp', UploadTemp),
	('/draw', DrawWindow),
	('/draw_beta', DrawWindow),
	('/del_thread', DelThread),
	('/edit_bbs', EditBbs),
	('/edit_thread_list', EditThreadList),
	('/update_bbs', UpdateBbs),
	('/edit_thread', EditThread),
	('/update_thread', UpdateThread),
	('/add_res', AddRes),
	('/add_tag', AddTag),
	('/del_res', DelRes),
	('/add_bookmark', AddBookmark),
	('/(mypage)',MyPage),
	('/(regist)',MyPage),
	('/ajax_ranking_update',SiteAnalyzer),
	('/applause',Applause),
	('/analyze',AnalyzeAccess),
	('/check_id',CheckId),
	('/draw_moper',MoperDraw),
	('/upload_moper',MoperUpload),
	('/moper_load',MoperLoad),
	('/moper_player',MoperPlayer),
	('/moper_import_raster',MoperImportRaster),
	('/moper_guide',MoperGuide),
	('/spam_check',SpamCheck),
	('/spam_delete',SpamDelete),
	('/admin',Admin),
	('/terms',Terms),
	('/search_tag',Pinterest),
	('/show_bookmark',ShowBookmark),
	('/move_account',MoveAccount),
	('/violation',ViolationTerms),
	('/update_profile',UpdateProfile),
	('/show_icon',ShowIcon),
	('/comic',Comic),
	('/scheme_update',SchemeUpdate),
	('/app',AppPortal),
	('/app/(.*)/img/(.*)',AppImage),
	('/api_feed',ApiFeed),
	('/api_user',ApiUser),
	('/api_bookmark',ApiBookmark),
	('/api_perpetuation',ApiPerpetuation),
	('/api_js',ApiJs),
	('/api_packed',ApiPacked),
	('/dev',DevPortal),
	('/stack_feed_worker',StackFeed),
	('/counter_worker',CounterWorker),
	('/feed_tweet',StackFeedTweet),
	('/ranking',RankingPortal),
	('/event_(.*)',EventList),
	],debug=False)

if __name__ == "__main__":
	main()


