#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#Pinterest表示
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging
import urllib
import math

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Counter import Counter
from myapp.Alert import Alert
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Entry import Entry
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.CssDesign import CssDesign
from myapp.BbsConst import BbsConst
from myapp.MappingThreadId import MappingThreadId
from myapp.MesThread import MesThread
from myapp.RecentTag import RecentTag
from myapp.ApiObject import ApiObject
from myapp.SearchTag import SearchTag
from myapp.ApiFeed import ApiFeed
from myapp.ApiUser import ApiUser
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.SiteAnalyzer import SiteAnalyzer
from myapp.ApiBookmark import ApiBookmark
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.Ranking import Ranking

class Pinterest(webapp.RequestHandler):
	@staticmethod
	def get_age(bookmark):
		if(bookmark):
			if(bookmark.birthday_year and bookmark.birthday_month and bookmark.birthday_day):
				return Pinterest._get_age_core(bookmark.birthday_year,bookmark.birthday_month,bookmark.birthday_day)
		return None

	@staticmethod
	def _get_age_core(bd_year,bd_month,bd_day):
		at=datetime.datetime.today().replace(tzinfo=UTC()).astimezone(JST())
		age = at.year - bd_year
		if (at.month, at.day) <= (bd_month, bd_day):
			age -= 1
		return age

	@staticmethod
	def is_following(user,user_id,view_mode):
		if(view_mode):
			if(user):
				my_bookmark=ApiObject.get_bookmark_of_user_id(user.user_id())
				if(my_bookmark):
					if(user_id in my_bookmark.user_list):
						return True
		return False

	@staticmethod
	def get_profile_for_edit(bookmark,view_mode):
		edit_profile="コメントを入力して下さい"
		if(bookmark):
			if(not view_mode):
				if(bookmark.profile):
					edit_profile=bookmark.profile
					compiled_line = re.compile("<br>")
					edit_profile = compiled_line.sub(r'\r\n', edit_profile)
		return edit_profile

	@staticmethod
	def consume_feed(user,view_mode,bookmark):
		new_feed_count=0
		if(not view_mode and bookmark and bookmark.new_feed_count):
			new_feed_count=bookmark.new_feed_count
		if(user and bookmark):
			if(not view_mode):
				if(bookmark.new_feed_count):
					bookmark.new_feed_count=0
					bookmark.put()
		return new_feed_count

	@staticmethod
	def get_tag_image(self,tag,page,unit):
		query = db.Query(MesThread,keys_only=True)
		#query.filter('illust_mode =', BbsConst.ILLUSTMODE_ILLUST)
		query.order('-create_date')
		query.filter('tag_list =', tag)
		cnt=query.count(limit=100)
		thread_key_list = query.fetch(limit=unit, offset=(page-1)*unit)
		thread_list=ApiObject.create_thread_object_list(self,thread_key_list,"pinterest")
		return {"thread_list":thread_list,"cnt":cnt}

	def get(self):
		Pinterest.get_core(self,False,False)

	@staticmethod
	def get_core(self,is_mypage,regist_finish):
		SetUtf8.set()

		unit=BbsConst.PINTEREST_PAGE_UNIT

		#メンテナンス画面
		is_maintenance=0
		if(MaintenanceCheck.is_appengine_maintenance()):
			is_maintenance=1
		
		#BBS COUNT
		cache=SiteAnalyzer.get_cache()
		bbs_n=cache["bbs_n"]
		illust_n=cache["illust_n"]

		#User
		user = users.get_current_user()

		login_flag=0
		if(user):
			login_flag=1

		order="new"
		if(self.request.get("order")):
			order=self.request.get("order")

		tab=None
		if(self.request.get("tab")):
			tab=self.request.get("tab")
		if(regist_finish):
			tab="bbs"
		
		page=1
		if(self.request.get("page")):
			page=int(self.request.get("page"))

		tag=""
		if(self.request.get("tag")):
			tag=self.request.get("tag")

		user_id=""
		if(self.request.get("user_id")):
			user_id=self.request.get("user_id")
		if user_id=="" and is_mypage and user:
			user_id=user.user_id()

		#マイユーザか
		view_mode=1
		if(user):
			if(user_id==user.user_id()):
				view_mode=0

		#プロフィール
		bookmark=None
		if(user_id):
			bookmark=ApiObject.get_bookmark_of_user_id(user_id)

		#プロフィールを編集
		edit_profile=Pinterest.get_profile_for_edit(bookmark,view_mode)

		#編集モードかどうか
		edit_mode=0
		if(self.request.get("edit")):
			edit_mode=int(self.request.get("edit"))

		#リダイレクト先API
		redirect_api="./"
		if(is_mypage):
			redirect_api="mypage"
		if(self.request.get("is_pinterest")):
			redirect_api="pinterest"
		search_api="pinterest"

		page_mode="index"
		view_user=None
		view_user_profile=None
		follow=None
		follower=None
		is_timeline_enable=0
		following=False
		bookmark_bbs_list=None
		rental_bbs_list=None
		illust_enable=True
		new_feed_count=0
		submit_illust_exist=True
		submit_illust_list=None
		age=None

		if(user_id!=""):
			if(not tab):
				tab="submit"
				new_feed_count=Pinterest.consume_feed(user,view_mode,bookmark)
				if(new_feed_count):
					tab="feed"

			if(tab=="bbs"):
				thread_list=None
				illust_enable=False
				bookmark_bbs_list=ApiBookmark.bookmark_get_bbs_list(self,user_id)
				rental_bbs_list=ApiUser.user_get_bbs_list(self,user_id)
	
			if(tab=="feed" or tab=="timeline"):
				thread_list=None
				is_timeline_enable=1
				illust_enable=False
	
			if(tab=="bookmark"):
				thread_list=ApiBookmark.bookmark_get_thread_list(self,user_id)
	
			if(tab=="submit"):
				thread_list=ApiUser.user_get_thread_list(self,user_id)
				submit_illust_list=thread_list
			
			#投稿したイラストが存在しない場合はブックマークを表示
			submit_illust_count=ApiUser.user_get_is_submit_thread_exist(self,user_id)
			if(submit_illust_count==0):
				submit_illust_exist=False
				if(tab=="submit"):
					tab="bookmark"
					thread_list=ApiBookmark.bookmark_get_thread_list(self,user_id)

			page_mode="user"
			view_user=ApiUser.user_get_user(self,user_id)
			view_user_profile=ApiUser.user_get_profile(self,user_id)
			tag_list=None#SearchTag.get_recent_tag("pinterest")
			next_query="user_id="+user_id+"&tab="+tab
			follow=ApiUser.user_get_follow(self,user_id,True)
			follower=ApiUser.user_get_follower(self,user_id,True)
			following=Pinterest.is_following(user,user_id,view_mode)
			age=Pinterest.get_age(bookmark)
		else:
			if(tag!=""):
				dic=Pinterest.get_tag_image(self,tag,page,unit)
				thread_list=dic["thread_list"]
				tag_list=SearchTag.update_recent_tag(tag,dic["cnt"],"pinterest")
				next_query="tag="+urllib.quote_plus(str(tag))
				page_mode="tag"
			else:
				if(order=="guide"):
					thread_list=None
					tag_list=None
					next_query=""
					page_mode="guide"
				else:
					thread_list=ApiFeed.feed_get_thread_list(self,order,(page-1)*unit,unit)
					tag_list=SearchTag.get_recent_tag("pinterest")
					next_query="order="+order

		#ログイン要求
		if(is_mypage and user_id==""):
			thread_list=None
			tag_list=None
			next_query=""
			page_mode="login_require"
			view_mode=0

		#ランキング
		user_rank=0
		if(bookmark):
			rank=Ranking.get_or_insert(BbsConst.THREAD_RANKING_KEY_NAME)
			user_rank=rank.get_user_rank(bookmark.user_id)

		#iPhoneかどうか
		is_iphone=CssDesign.is_iphone(self)

		template_values = {
			'host': "./",
			'user': user,
			'order': order,
			'tag_list': tag_list,
			'thread_list': thread_list,
			'redirect_url': self.request.path,
			'next_page': page+1,
			'next_query': next_query,
			'page_mode': page_mode,
			'tag': tag,
			'view_user': view_user,
			'view_user_profile': view_user_profile,
			'is_iphone': is_iphone,
			'bbs_n': bbs_n,
			'illust_n': illust_n,
			'user_id': user_id,
			'follow': follow,
			'follower': follower,
			'view_mode': view_mode,
			'edit_mode': edit_mode,
			'tab': tab,
			'login_flag': login_flag,
			'bookmark': bookmark,
			'is_timeline_enable': is_timeline_enable,
			'following':following,
			'bookmark_bbs_list': bookmark_bbs_list,
			'rental_bbs_list': rental_bbs_list,
			'illust_enable': illust_enable,
			'edit_profile': edit_profile,
			'redirect_url': self.request.path,
			'new_feed_count': new_feed_count,
			'submit_illust_exist': submit_illust_exist,
			'regist_finish': regist_finish,
			'is_maintenance': is_maintenance,
			'redirect_api': redirect_api,
			'search_api': search_api,
			'age': age,
			'user_rank': user_rank
		}
		path = os.path.join(os.path.dirname(__file__), '../html/pinterest.html')
		self.response.out.write(template.render(path, template_values))

