#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#マイページ、ソーシャル風
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

webapp.template.register_template_library('templatetags.django_filter')

from Analyze import Analyze
from Bbs import Bbs
from Entry import Entry
from Counter import Counter
from Response import Response
from MesThread import MesThread
from BbsConst import BbsConst
from ThreadImage import ThreadImage

from SetUtf8 import SetUtf8
from RecentCommentCache import RecentCommentCache
from MappingId import MappingId
from SpamCheck import SpamCheck
from SpamDelete import SpamDelete
from AddNewThread import AddNewThread
from Alert import Alert
from OwnerCheck import OwnerCheck
from UpdateBbs import UpdateBbs
from AddEntry import AddEntry
from Admin import Admin
from PageGenerate import PageGenerate
from SearchUser import SearchUser
from Applause import Applause
from RssFeed import RssFeed
from ShowThread import ShowThread
from ShowBbs import ShowBbs
from MoveAccount import MoveAccount
from MaintenanceCheck import MaintenanceCheck
from MoperUpload import MoperUpload
from MoperImportRaster import MoperImportRaster
from MoperGuide import MoperGuide
from MoperLoad import MoperLoad
from MoperPlayer import MoperPlayer
from MoperDraw import MoperDraw
from LocalToolDraw import LocalToolDraw
from LocalTool import LocalTool
from Embedded import Embedded
from AnalyzeAccess import AnalyzeAccess
from CssDesign import CssDesign
from ImageFile import ImageFile
from UpdateThread import UpdateThread
from EditThread import EditThread
from ViolationTerms import ViolationTerms
from MappingThreadId import MappingThreadId
from DrawWindow import DrawWindow
from AddTag import AddTag
from SearchTag import SearchTag
from Bookmark import Bookmark
from AddBookmark import AddBookmark
from NicoTracker import NicoTracker
from UpdateProfile import UpdateProfile
from Alert import Alert
from StackFeedData import StackFeedData
from ApiObject import ApiObject
from OwnerCheck import OwnerCheck

class MyPage(webapp.RequestHandler):
	@staticmethod
	def get_age(bd_year,bd_month,bd_day):
		at=datetime.datetime.today()
		age = at.year - bd_year
		if (at.month, at.day) <= (bd_month, bd_day):
			age -= 1
		return age

	def withdraw(self,bookmark,your_bbs_count):
		user_id=self.request.get("user_id")
		if(not user_id):
			self.response.out.write(Alert.alert_msg("ユーザIDが必要です。",self.request.host))
			return True

		user=users.get_current_user()
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user_id)	#キャッシュから取得するのを防止
		if(not bookmark):
			self.response.out.write(Alert.alert_msg("ユーザが見つかりません。",self.request.host))
			return True

		if(OwnerCheck.check_bookmark(bookmark,user)):
			self.response.out.write(Alert.alert_msg("退会する権限がありません。",self.request.host))
			return True

		if(your_bbs_count==0):
			bookmark.delete()
			self.response.out.write(Alert.alert_msg("退会が完了しました。",self.request.host));
		else:
			self.response.out.write(Alert.alert_msg("退会する前にレンタルしている掲示板を削除する必要があります。残り："+str(your_bbs_count),self.request.host))
			return True

		return True

	def get(self,regist_mode):
		SetUtf8.set()

		#表示モードかどうか
		view_mode=None
		if(self.request.get("user")):
			view_mode=self.request.get("user")
		
		#ユーザ検索
		if(self.request.get("user_id")):
			target_bookmark=ApiObject.get_bookmark_of_user_id(self.request.get("user_id"))
			if(target_bookmark==None):
				self.response.out.write(Alert.alert_msg("ユーザが見つかりません。",self.request.host))
				return
			view_mode=str(target_bookmark.key());
		
		#リダイレクトURL
		host="http://"+MappingId.mapping_host(self.request.host)+"/";
		redirect_url=host+"mypage";
	
		#編集モードか
		edit_mode=0
		if(self.request.get("edit")):
			edit_mode=int(self.request.get("edit"))
	
		#掲示板一覧
		user = users.get_current_user()
		favorite=""
		bookmark=None

		#管理人かどうか
		is_admin=0
		if(OwnerCheck.is_admin(user) and self.request.get("is_admin")):
			is_admin=1

		#自分だったらビューモードにしない
		if(user and self.request.get("user_id")==user.user_id() and not self.request.get("withdraw")):
			view_mode=0
			#self.redirect(str("./mypage"))
			#return
		
		#ログインしているか
		login_flag=0
		if(user):
			login_flag=1

		#表示設定
		if(view_mode):
			bookmark=db.get(view_mode)
		else:
			if user:
				bookmark=ApiObject.get_bookmark_of_user_id(user.user_id())
			else:
				bookmark=None

		#掲示板の新規作成が完了したか
		regist_finish=False
		if(regist_mode=="regist"):
			regist_finish=True
		
		#プロフィールを編集
		edit_profile="None"
		if(bookmark):
			if(not view_mode):
				if(bookmark.profile):
					edit_profile=bookmark.profile
					compiled_line = re.compile("<br>")
					edit_profile = compiled_line.sub(r'\r\n', edit_profile)
		
		#退会
		if(self.request.get("withdraw") and self.request.get("withdraw")=="go"):
			if(not bookmark):
				self.response.out.write(Alert.alert_msg("ユーザ情報は未登録です。",self.request.host));
				return
			your_bbs_count=Bbs.all().filter("del_flag =",0).filter("user_id =",bookmark.user_id).count()
			if(self.withdraw(bookmark,your_bbs_count)):
				return;
		
		#タブ
		tab=self.request.get("tab")
		if(not tab):
			tab="profile"

		#ページ
		feed_page=1
		if(self.request.get("feed_page")):
			feed_page=int(self.request.get("feed_page"))
		
		feed_page_n=1
		feed_page_unit=10
		if(bookmark and bookmark.stack_feed_list):
			feed_page_n=(len(bookmark.stack_feed_list)+(feed_page_unit-1))/feed_page_unit
		
		#iPhoneモードかどうか
		is_iphone=CssDesign.is_iphone(self)
		
		#年齢
		age=None
		if(bookmark):
			if(bookmark.birthday_year and bookmark.birthday_month and bookmark.birthday_day):
				age=MyPage.get_age(bookmark.birthday_year,bookmark.birthday_month,bookmark.birthday_day)
		
		#フィードURL
		feed_previous_page=host+"mypage?"
		if(view_mode and bookmark):
			feed_previous_page+="user_id="+bookmark.user_id+"&"
		feed_previous_page+="tab=feed&feed_page="
		feed_next_page=feed_previous_page+str(feed_page+1)
		feed_previous_page=feed_previous_page+str(feed_page-1)
		if(feed_page==feed_page_n):
			feed_next_page=""
		
		template_values = {
			'host': host,
			'user':user,
			'regist_finish':regist_finish,
			'bookmark': bookmark,
			'edit_profile': edit_profile,
			'view_mode': view_mode,
			'edit_mode': edit_mode,
			'is_iphone': is_iphone,
			'tab': tab,
			'age': age,
			'feed_page': feed_page,
			'feed_previous_page': feed_previous_page,
			'feed_next_page': feed_next_page,
			'feed_page_n': feed_page_n,
			'login_flag': login_flag,
			'is_admin': is_admin,
			'redirect_url': self.request.path
		}
		
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_mypage.html')
		self.response.out.write(template.render(path, template_values))
		
		if(user and bookmark):
			if(not view_mode):
				if(tab=="feed" and bookmark.new_feed_count):
					bookmark.new_feed_count=0
					bookmark.put()
			
