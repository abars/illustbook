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
from myapp.LocalToolDraw import LocalToolDraw
from myapp.LocalTool import LocalTool
from myapp.Embedded import Embedded
from myapp.AnalyzeAccess import AnalyzeAccess
from myapp.CssDesign import CssDesign
from myapp.ImageFile import ImageFile
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
from myapp.Alert import Alert
from myapp.StackFeedData import StackFeedData
from myapp.ApiObject import ApiObject
from myapp.OwnerCheck import OwnerCheck
from myapp.Ranking import Ranking
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.Pinterest import Pinterest

class MyPage(webapp.RequestHandler):
	@staticmethod
	def get_age(bd_year,bd_month,bd_day):
		at=datetime.datetime.today().replace(tzinfo=UTC()).astimezone(JST())
		age = at.year - bd_year
		if (at.month, at.day) <= (bd_month, bd_day):
			age -= 1
		return age

	def delete_user_thread(self,user_id):
		query=MesThread.all().filter("user_id =",user_id)
		thread_list=query.fetch(limit=1000)
		for thread in thread_list:
			thread.delete()

	def withdraw(self,bookmark,your_bbs_count):
		user_id=self.request.get("user_id")
		if(not user_id):
			Alert.alert_msg_with_write(self,"ユーザIDが必要です。")
			return True

		user=users.get_current_user()
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user_id)	#キャッシュから取得するのを防止
		if(not bookmark):
			Alert.alert_msg_with_write(self,"ユーザが見つかりません。")
			return True

		if(OwnerCheck.check_bookmark(bookmark,user)):
			Alert.alert_msg_with_write(self,"退会する権限がありません。")
			return True

		if(your_bbs_count==0):
			#delete_user_thread(user.user_id())	#他人の掲示板に描いたイラストは慎重に削除する必要がある気がする
			bookmark.delete()
			Alert.alert_msg_with_write(self,"退会が完了しました。");
		else:
			Alert.alert_msg_with_write(self,"退会する前にレンタルしている掲示板を削除する必要があります。<BR>掲示板の削除はマイページのイラストタブで編集を押すことで行うことができます。<BR>残りの掲示板数："+str(your_bbs_count))
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
				Alert.alert_msg_with_write(self,"ユーザが見つかりません。")
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
		edit_profile=Pinterest.get_profile_for_edit(bookmark,view_mode)
		
		#退会
		if(self.request.get("withdraw") and self.request.get("withdraw")=="go"):
			if(not bookmark):
				Alert.alert_msg_with_write(self,"ユーザ情報は未登録です。");
				return
			your_bbs_count=Bbs.all().filter("del_flag =",0).filter("user_id =",bookmark.user_id).count()
			if(self.withdraw(bookmark,your_bbs_count)):
				return;

		#リダイレクト
		if(BbsConst.PINTEREST_MODE):
			if(user and OwnerCheck.is_admin(user)):
				return Pinterest.get_core(self,True)
		
		#タブ
		tab=self.request.get("tab")
		if(not tab):
			tab="illust"
			if(not view_mode and bookmark and bookmark.new_feed_count):
				tab="feed"

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
		
		#フォロー中かどうか
		following=False
		if(bookmark):
			following=Pinterest.is_following(user,bookmark.user_id,view_mode)

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
		
		#ランキング
		user_rank=0
		owner_rank=0
		if(bookmark):
			rank=Ranking.get_or_insert(BbsConst.THREAD_RANKING_KEY_NAME)
			user_rank=rank.get_user_rank(bookmark.user_id)
			owner_rank=rank.get_owner_rank(bookmark.user_id)
		
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
			'redirect_url': self.request.path,
			'mypage': not view_mode,
			'following': following,
			'user_rank': user_rank,
			'owner_rank': owner_rank
		}
		
		path = os.path.join(os.path.dirname(__file__), '../html/mypage.html')
		self.response.out.write(template.render(path, template_values))
		
		if(user and bookmark):
			if(not view_mode):
				if(tab=="feed" and bookmark.new_feed_count):
					bookmark.new_feed_count=0
					bookmark.put()
			
