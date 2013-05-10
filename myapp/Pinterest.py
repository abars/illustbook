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

import template_select

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

#from django.utils.html import strip_spaces_between_tags

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
from myapp.SearchThread import SearchThread

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
	def _get_new_feed_count(user,view_mode,bookmark):
		new_feed_count=0
		if(not view_mode and bookmark and bookmark.new_feed_count):
			new_feed_count=bookmark.new_feed_count
		return new_feed_count

	@staticmethod
	def _consume_feed(user,view_mode,bookmark):
		if(user and bookmark):
			if(not view_mode):
				if(bookmark.new_feed_count):
					bookmark.new_feed_count=0
					bookmark.put()

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
		Pinterest.get_core(self,Pinterest.PAGE_MODE_NORMAL)

	PAGE_MODE_NORMAL=0
	PAGE_MODE_MYPAGE=1
	PAGE_MODE_GUIDE=2
	PAGE_MODE_REGIST=3
	PAGE_MODE_BOOKMARK=4

	@staticmethod
	def get_core(self,request_page_mode):
		SetUtf8.set()

		unit=BbsConst.PINTEREST_PAGE_UNIT

		user = users.get_current_user()

		search=None
		if(self.request.get("search")):
			search=self.request.get("search")
		
		page=1
		if(self.request.get("page")):
			page=int(self.request.get("page"))

		tag=""
		if(self.request.get("tag")):
			tag=self.request.get("tag")

		user_id=""
		if(self.request.get("user_id")):
			user_id=self.request.get("user_id")
		if user_id=="" and (request_page_mode==Pinterest.PAGE_MODE_MYPAGE or request_page_mode==Pinterest.PAGE_MODE_REGIST) and user:
			user_id=user.user_id()

		#リダイレクト先API
		redirect_api="./"
		if(request_page_mode==Pinterest.PAGE_MODE_MYPAGE or request_page_mode==Pinterest.PAGE_MODE_REGIST):
			redirect_api="mypage"

		#コンテンツのみを供給するか
		contents_only=None
		if(self.request.get("contents_only")):
			contents_only=True

		if(user_id!=""):
			Pinterest._user_page(self,user,user_id,page,request_page_mode,redirect_api,contents_only)
			return
		if(request_page_mode==Pinterest.PAGE_MODE_BOOKMARK):
			Pinterest._bookmark(self,user,user_id,page,request_page_mode,redirect_api,contents_only)
			return
		if(request_page_mode==Pinterest.PAGE_MODE_GUIDE):
			Pinterest._guide(self,user,user_id,page,request_page_mode,redirect_api,contents_only)
			return
		if(tag!=""):
			Pinterest._tag_search(self,tag,user,user_id,page,request_page_mode,redirect_api,contents_only)
			return
		if(search):
			Pinterest._text_search(self,search,user,user_id,page,request_page_mode,redirect_api,contents_only)
			return
		if(request_page_mode==Pinterest.PAGE_MODE_MYPAGE and user_id==""):
			Pinterest._login_require(self,user,user_id,page,request_page_mode,redirect_api,contents_only)
			return

		Pinterest._index(self,user,user_id,page,request_page_mode,redirect_api,contents_only)
		return

	@staticmethod
	def initialize_template_value(self,user,user_id,page,request_page_mode,redirect_api,contents_only):
		search_api="search_tag"

		template_values = {
			'user': user,
			'order': None,
			'tag_list': None,
			'thread_list': None,
			'redirect_url': self.request.path,
			'page': page,
			'next_page': page+1,
			'next_query': "",
			'tag': None,
			'user_id': user_id,
			'tab': None,
			'bookmark': None,
			'illust_enable': False,
			'redirect_url': self.request.path,
			'regist_finish': False,
			'redirect_api': redirect_api,
			'search_api': search_api,
			'contents_only': contents_only,
			'search': None,
			'top_page': False
		}
		return template_values

	@staticmethod
	def _index(self,user,user_id,page,request_page_mode,redirect_api,contents_only):
		template_values=Pinterest.initialize_template_value(self,user,user_id,page,request_page_mode,redirect_api,contents_only)

		unit=BbsConst.PINTEREST_PAGE_UNIT

		order="new"
		if(self.request.get("order")):
			order=self.request.get("order")

		search_api="search_tag"

		template_values['thread_list']=ApiFeed.feed_get_thread_list(self,order,(page-1)*unit,unit)
		template_values['next_query']="order="+order
		template_values['tag_list']=SearchTag.get_recent_tag(search_api)
		template_values['top_page']=True
		template_values['order']=order
		template_values['page_mode']="index"
		template_values['illust_enable']=True

		Pinterest._render_page(self,template_values)

	@staticmethod
	def _text_search(self,search,user,user_id,page,request_page_mode,redirect_api,contents_only):
		template_values=Pinterest.initialize_template_value(self,user,user_id,page,request_page_mode,redirect_api,contents_only)

		search_api="search_tag"
		unit=BbsConst.PINTEREST_PAGE_UNIT

		thread_list=SearchThread.search(search,page,unit,BbsConst.SEARCH_THREAD_INDEX_NAME)
		thread_list=ApiObject.create_thread_object_list(self,thread_list,"search")

		template_values['thread_list']=thread_list
		template_values['next_query']="search="+urllib.quote_plus(str(search))
		template_values['tag_list']=SearchTag.get_recent_tag(search_api)
		template_values['page_mode']="search"
		template_values['illust_enable']=True
		template_values['search']=search

		Pinterest._render_page(self,template_values)

	@staticmethod
	def _tag_search(self,tag,user,user_id,page,request_page_mode,redirect_api,contents_only):
		template_values=Pinterest.initialize_template_value(self,user,user_id,page,request_page_mode,redirect_api,contents_only)

		search_api="search_tag"
		unit=BbsConst.PINTEREST_PAGE_UNIT
		dic=Pinterest.get_tag_image(self,tag,page,unit)
		template_values['thread_list']=dic["thread_list"]
		template_values['tag_list']=SearchTag.update_recent_tag(tag,dic["cnt"],search_api)
		template_values['next_query']="tag="+urllib.quote_plus(str(tag))
		template_values['page_mode']="tag"
		template_values['illust_enable']=True
		template_values['search']=tag

		Pinterest._render_page(self,template_values)

	@staticmethod
	def _login_require(self,user,user_id,page,request_page_mode,redirect_api,contents_only):
		template_values=Pinterest.initialize_template_value(self,user,user_id,page,request_page_mode,redirect_api,contents_only)
		template_values['page_mode']="login_require"

		Pinterest._render_page(self,template_values)

	@staticmethod
	def _guide(self,user,user_id,page,request_page_mode,redirect_api,contents_only):
		template_values=Pinterest.initialize_template_value(self,user,user_id,page,request_page_mode,redirect_api,contents_only)

		cache=SiteAnalyzer.get_cache()
		template_values["bbs_n"]=cache["bbs_n"]
		template_values["illust_n"]=cache["illust_n"]
		template_values['page_mode']="guide"

		Pinterest._render_page(self,template_values)

	@staticmethod
	def _bookmark(self,user,user_id,page,request_page_mode,redirect_api,contents_only):
		template_values=Pinterest.initialize_template_value(self,user,user_id,page,request_page_mode,redirect_api,contents_only)

		thread=None
		if(self.request.get("thread_key")):
			try:
				thread = db.get(self.request.get("thread_key"))
			except:
				thread=None

		bbs=None
		if(self.request.get("bbs_key")):
			try:
				bbs = db.get(self.request.get("bbs_key"))
			except:
				bbs=None

		app=None
		if(self.request.get("app_key")):
			try:
				app = db.get(self.request.get("app_key"))
			except:
				app=None
		
		cache=SiteAnalyzer.get_cache()
		template_values["search_thread"]=thread
		template_values["search_bbs"]=bbs
		template_values["search_app"]=app
		template_values['page_mode']="bookmark"

		Pinterest._render_page(self,template_values)

	@staticmethod
	def _decide_default_tab(self,bookmark_illust_exist,submit_illust_exist,view_mode,bookmark,user,request_page_mode):
		#掲示板作成完了時はbbsに飛ばす
		if(request_page_mode==Pinterest.PAGE_MODE_REGIST):
			return "bbs"

		#タブの取得
		tab=self.request.get("tab")
		if(tab):
			return tab

		#タブ指定なしでフィードが存在する場合はフィードに飛ばす

		#デフォルトタブの決定
		if(not tab and Pinterest._get_new_feed_count(user,view_mode,bookmark)):
			return "feed"

		#投稿したイラストもブックマークしたイラストも存在しない場合
		if((not submit_illust_exist) and (not bookmark_illust_exist)):
			#自分の場合は掲示板、他人の場合はフィードを表示
			if(view_mode):
				return "feed"
			return "bbs"
		
		#投稿したイラストかブックマークしたイラストが存在する場合はそれを表示
		if(submit_illust_exist):
			return "submit"
		if(bookmark_illust_exist):
			return "bookmark"

		return None

	@staticmethod
	def _user_page(self,user,user_id,page,request_page_mode,redirect_api,contents_only):
		illust_enable=False
		submit_illust_exist=True
		bookmark_illust_exist=True
		thread_list=None

		#プロフィール
		bookmark=None
		if(user_id):
			bookmark=ApiObject.get_bookmark_of_user_id(user_id)

		#イラストの存在を検出
		submit_illust_count=ApiUser.user_get_is_submit_thread_exist(self,user_id)
		bookmark_illust_count=ApiBookmark.bookmark_get_is_bookmark_thread_exist(self,user_id,bookmark)
		if(bookmark_illust_count==0):
			bookmark_illust_exist=False
		if(submit_illust_count==0):
			submit_illust_exist=False

		#マイユーザか
		view_mode=1
		if(user):
			if(user_id==user.user_id()):
				view_mode=0

		#タブ
		tab=Pinterest._decide_default_tab(self,bookmark_illust_exist,submit_illust_exist,view_mode,bookmark,user,request_page_mode)

		#フィード数の消化
		new_feed_count=Pinterest._get_new_feed_count(user,view_mode,bookmark)
		if(tab=="feed"):
			Pinterest._consume_feed(user,view_mode,bookmark)

		#プロフィールを編集
		edit_profile=Pinterest.get_profile_for_edit(bookmark,view_mode)

		#編集モードかどうか
		edit_mode=0
		if(self.request.get("edit")):
			edit_mode=int(self.request.get("edit"))

		bookmark_bbs_list=None
		rental_bbs_list=None
		if(tab=="bbs"):
			thread_list=None
			illust_enable=False
			bookmark_bbs_list=ApiBookmark.bookmark_get_bbs_list(self,user_id)
			rental_bbs_list=ApiUser.user_get_bbs_list(self,user_id)
		
		is_timeline_enable=0
		if(tab=="feed" or tab=="timeline"):
			thread_list=None
			is_timeline_enable=1
			illust_enable=False
	
		if(tab=="bookmark"):
			thread_list=ApiBookmark.bookmark_get_thread_list(self,user_id,bookmark)
	
		if(tab=="submit"):
			#イラストが消去されている場合を考慮してスレッドが見つかるまでページを進める
			max_page=(submit_illust_count+BbsConst.PINTEREST_MYPAGE_PAGE_UNIT-1)/BbsConst.PINTEREST_MYPAGE_PAGE_UNIT
			thread_list=[]
			while(page<=max_page):
				limit=BbsConst.PINTEREST_MYPAGE_PAGE_UNIT
				offset=limit*(page-1)
				thread_list=ApiUser.user_get_thread_list_core(self,user_id,offset,limit)
				if(len(thread_list)>=1):
					break
				page=page+1

			submit_illust_list=thread_list
			
		page_mode="user"
		view_user=ApiUser.user_get_user(self,user_id,bookmark)
		view_user_profile=ApiUser.user_get_profile(self,user_id,bookmark)
		tag_list=None
		next_query="user_id="+user_id+"&tab="+tab+"&edit="+str(edit_mode)
		
		only_icon=True
		if(edit_mode):
			only_icon=False

		follow=ApiUser.user_get_follow(self,user_id,only_icon,bookmark)
		follower=ApiUser.user_get_follower(self,user_id,only_icon)
		following=Pinterest.is_following(user,user_id,view_mode)
		age=Pinterest.get_age(bookmark)

		#ランキング
		user_rank=0
		if(bookmark):
			rank=Ranking.get_by_key_name(BbsConst.THREAD_RANKING_KEY_NAME)
			if(rank):
				user_rank=rank.get_user_rank(bookmark.user_id)

		detail_exist=False
		if(bookmark):
			if(bookmark.sex or age):
				detail_exist=True
			if(bookmark.birthday_month or bookmark.birthday_day or bookmark.birthday_year):
				detail_exist=True
			if(bookmark.homepage or bookmark.mail or bookmark.twitter_id):
				detail_exist=True

		#凍結
		if(bookmark and bookmark.frozen):
			thread_list=None

		template_values = {
			'user': user,
			'thread_list': thread_list,
			'redirect_url': self.request.path,
			'page': page,
			'next_page': page+1,
			'next_query': next_query,
			'page_mode': page_mode,
			'tag': None,
			'view_user': view_user,
			'view_user_profile': view_user_profile,
			'user_id': user_id,
			'follow': follow,
			'follower': follower,
			'view_mode': view_mode,
			'edit_mode': edit_mode,
			'tab': tab,
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
			'bookmark_illust_exist': bookmark_illust_exist,
			'regist_finish': (request_page_mode==Pinterest.PAGE_MODE_REGIST),
			'redirect_api': redirect_api,
			'age': age,
			'user_rank': user_rank,
			'contents_only': contents_only,
			'search': None,
			'top_page': False,
			'detail_exist': detail_exist,
			'is_admin': OwnerCheck.is_admin(user)
		}
		Pinterest._render_page(self,template_values)

	@staticmethod
	def _render_page(self,template_values):
		template_values['host']="./"
		template_values['is_iphone']=CssDesign.is_iphone(self)
		template_values['is_tablet']=CssDesign.is_tablet(self)
		template_values['tag_display_n']=5
		template_values['is_maintenance']=MaintenanceCheck.is_appengine_maintenance()
		if(template_values['user']):
			template_values['login_flag']=1
		else:
			template_values['login_flag']=0
		render=template_select.render("/html/pinterest.html", template_values)
		#render=strip_spaces_between_tags(render)
		self.response.out.write(render)



