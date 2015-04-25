#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板を表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging
import urllib

from google.appengine.api.labs import taskqueue

import template_select
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
from myapp.OwnerCheck import OwnerCheck
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.BbsConst import BbsConst
from myapp.MesThread import MesThread
from myapp.PageGenerate import PageGenerate
from myapp.RecentCommentCache import RecentCommentCache
from myapp.Analyze import Analyze
from myapp.Entry import Entry
from myapp.CssDesign import CssDesign
from myapp.ApiObject import ApiObject
from myapp.CounterWorker import CounterWorker
from myapp.ShowEntry import ShowEntry
from myapp.CategoryList import CategoryList

class ShowBbs(webapp.RequestHandler):
	def get(self,bbs_key):
		#日本語対応
		SetUtf8.set()

		#英語版かどうか
		is_english=CssDesign.is_english(self)

		
		#メンテナンス中かどうか
		is_maintenance=0
		if(MaintenanceCheck.is_appengine_maintenance()):
			is_maintenance=1

		#掲示板を取得
		bbs=ShowBbs.get_bbs(self,bbs_key)
		if(bbs==None):
			return

		#掲示板削除チェック
		if(bbs.del_flag) :
			if(is_english):
				Alert.alert_msg_with_write(self,"This bbs was deleted.")
			else:
				Alert.alert_msg_with_write(self,"この掲示板は削除されました。")
			return

		#ページ取得
		page = 1
		if self.request.get("page"):
			try:
				page = int(self.request.get("page"))
			except:
				Alert.alert_msg_with_write(self,"ページ番号が異常です。")
				return
			if page<1 :
				page=1

		#描画順を取得
		order=ShowBbs.get_order(self,bbs)
		
		#カテゴリ取得
		category=""
		if(self.request.get("category")):
			category=self.request.get("category")
		
		#スレッド一覧を取得
		thread_query=ShowBbs.get_thread_query(bbs,category,order)
		
		#1ページのイラスト数を取得
		col_num=ShowBbs.get_col_num(bbs,order)

		#スレッド数とスレッドを取得
		count_limit=(BbsConst.PAGE_LIST_COUNT+page)*col_num	#ページ番号生成用にしか使わないのでページ番号のMaxがわかれば良い
		if(category==""):
			threads_num = bbs.cached_threads_num
		else:
			threads_num = thread_query.count(limit=count_limit)
		all_threads = thread_query.fetch(limit=col_num, offset=(page-1)*col_num)
		
		#返信イラストを取得
		all_entries = None
		#if(order=="thumbnail"):
		#	all_entries=ShowBbs.get_illust_reply(bbs,page,col_num)
		#	if(threads_num<all_entries["count"]):
		#		threads_num=all_entries["count"]
		#	all_entries=all_entries["entry"]
		
		#ホストURLを取得
		host_url="http://"+MappingId.mapping_host(self.request.host)+"/";
		
		#URLを作成
		mapped_category=urllib.quote(category.encode('utf-8'))
		page_url=MappingId.get_usr_url(host_url,bbs)
		page_url_base=MappingId.get_usr_url(host_url,bbs)+'?order='+order+'&amp;category='+mapped_category+'&amp;page='
		page_url_order_base=MappingId.get_usr_url(host_url,bbs)+'?page=1&amp;category='+mapped_category+'&amp;order='
		page_url_category_base=MappingId.get_usr_url(host_url,bbs)+'?page=1&amp;order='+order+"&amp;category="

		#ページリストを作成
		page_list=PageGenerate.generate_page(page,threads_num,col_num)
		
		#ログインユーザを取得
		user = users.get_current_user()

		logined=0
		if(user):
			logined=1
		
		owner=user
		if(OwnerCheck.check(bbs,user)):
			owner=None
		
		#サイドバーコメントを取得
		side_comment=RecentCommentCache.get_entry(bbs)
		side_thread=RecentCommentCache.get_thread(bbs)
		
		#カテゴリ一覧を取得
		category_list=None
		if(bbs.category_list):
			if(bbs.category_list!=""):
				category_list=CategoryList.get_category_list(bbs) #bbs.category_list.split(",")

		#ページデザインを取得
		css_key=self.request.get("css_key")
		design=CssDesign.get_design_object(self,bbs,host_url,0)

		#サイドバー一覧を作成
		sidebar_list=ShowBbs.get_sidebar(bbs,category_list,side_comment,side_thread)

		#新規スレッドを作成できるか
		can_create_thread=ShowBbs.get_can_create_thread(bbs,user,logined)
		can_create_new_image=ShowBbs.get_can_create_new_image(bbs,owner)

		#スレッドを全て取得
		all_threads_cached=ApiObject.get_cached_object_list(all_threads)
		
		#コメントフォームを表示するか
		show_comment_form=1
		if(bbs.comment_login_require and not(owner)):
			show_comment_form=0

		#フルコメントデバッグ
		if(self.request.get("full_comment")):
			bbs.enable_full_comment=1

		#フルフラット表示をデフォルト化
		if(bbs.bbs_mode==BbsConst.BBS_MODE_NO_IMAGE):
			bbs.enable_full_flat=0
			bbs.enable_full_comment=0
		else:
			bbs.enable_full_flat=1
			#bbs.enable_full_comment=1 #デフォルト化を止める

		#コメントを全て取得
		#user_name=""
		user_name=ShowEntry.get_user_name(user)
		if(bbs.enable_full_comment):
			admin_user=OwnerCheck.is_admin(user)
			ShowEntry.render_comment_list(self,all_threads_cached,host_url,bbs,show_comment_form,logined,admin_user,user_name,user)

		#デザインの編集ができるか
		can_edit_design=False
		is_admin=OwnerCheck.is_admin(user)
		if(owner or (is_admin and bbs.bbs_mode==BbsConst.BBS_MODE_EVERYONE)):
			can_edit_design=True

		#infinite_scrollを使用するかどうか
		infinite_scroll=False
		#if(bbs.bbs_mode!=BbsConst.BBS_MODE_NO_IMAGE):# and design["is_iphone"]):
		infinite_scroll=True

		#infinite_scrollの2ページ目以降
		contents_only=0
		if(self.request.get("contents_only")=="1"):
			contents_only=1

		#メッセージ
		message=memcache.get(BbsConst.OBJECT_BBS_MESSAGE_HEADER+str(bbs.key()))

		#カウントアップコメント
		if(bbs.counter):
			bbs.counter.new_day_update()
		count_up_comment=None
		#if(bbs.dont_count_owner):
		#	if(owner):
		#		count_up_comment="管理人"
		#	else:
		#		count_up_comment="ユーザ"

		#カテゴリリスト
		show_category_list=False
		if(self.request.get("show_category_list")=="1"):
			show_category_list=True

		#レンダリング
		template_values = {
			'host': host_url,
			'usrhost': MappingId.get_usr_url(host_url,bbs),
			'threads': all_threads_cached,
			'all_entries':all_entries,
			'bbs':bbs,
			'new_url': 'create_new_thread',
			'page':page,
			'page_url':page_url,
			'page_url_base':page_url_base,
			'order':order,
			'page_url_order_base':page_url_order_base,
			'page_list':page_list,
			'user':user,
			'owner': owner,
			'side_comment':side_comment,
			'side_thread':side_thread,
			'logined':logined,
			'can_create_thread':can_create_thread,
			'category_list':category_list,
			'page_url_category_base':page_url_category_base,
			'now_category':category,
			'can_create_new_image':can_create_new_image,
			'template_path':design["template_path"],
			'css_name':design["css_name"],
			'is_iphone':design["is_iphone"],
			'is_tablet':design["is_tablet"],
			'template_base_color':design["template_base_color"],
			'sidebar_list': sidebar_list,
			'is_maintenance': is_maintenance,
			'css_key': css_key,
			'redirect_url': self.request.path,
			'show_comment_form': show_comment_form,
			'user_name': user_name,
			'is_admin': is_admin,
			'can_edit_design': can_edit_design,
			'infinite_scroll': infinite_scroll,
			'infinite_scroll_selecter': ".entry",
			'contents_only': contents_only,
			'message': message,
			'is_english': is_english,
			'count_up_comment': count_up_comment,
			'show_category_list': show_category_list
		}

		path = "/html/"+design["base_name"]
		self.response.out.write(template_select.render(path, template_values))
		
		if(is_maintenance):
			return
		
		CounterWorker.update_counter(self,bbs,None,owner)

	@staticmethod
	def get_sidebar(bbs,category_list,side_comment,side_thread):
		sidebar_list=[]
		if(bbs.freearea):
			sidebar_list.append("free")
		if(bbs.amazon):
			sidebar_list.append("affiliate")
		if(side_thread):
			sidebar_list.append("thread")
		if(side_comment):
			sidebar_list.append("comment")
		if(category_list):
			sidebar_list.append("category")
		if(not bbs.disable_counter):
			sidebar_list.append("counter")
		sidebar_list.append("menu")
		if(bbs.twitter_enable):
			sidebar_list.append("twitter")
		return sidebar_list

	@staticmethod
	def get_can_create_thread(bbs,user,logined):
		can_create_thread=0
		if(not bbs.disable_create_new_thread):
			can_create_thread=1
		if(bbs.disable_create_new_thread==1 and user):
			can_create_thread=1
		if(bbs.disable_create_new_thread==2 and logined):
			can_create_thread=1
		return can_create_thread

	@staticmethod
	def get_can_create_new_image(bbs,user):
		can_create_new_image=0
		if(bbs.bbs_mode==1):
			can_create_new_image=1
		if(bbs.bbs_mode==2 and user):
			can_create_new_image=1
		return can_create_new_image

	@staticmethod
	def get_thread_query(bbs,category,order):
		thread_query = db.Query(MesThread,keys_only=True)
		thread_query.filter('bbs_key =', bbs)
		if(bbs.show_only_movie):
			if(order=="illust"):
				thread_query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
			else:
				thread_query.filter("illust_mode =",BbsConst.ILLUSTMODE_MOPER)
		if(category!=""):
			thread_query.filter("category =",category)
		if(order=="new"):
			thread_query.order('-create_date')
		else:
			if(order=="comment"):
				thread_query.order('-comment_cnt')
			else:
				if(order=="applause"):
					thread_query.order('-applause')
				else:
					thread_query.order('-date')
		return thread_query

	@staticmethod
	def get_bbs(req,bbs_key):
		bbs_key=MappingId.mapping(bbs_key)
		if(bbs_key==""):
			Alert.alert_msg_notfound(req)
			return None
		bbs=ApiObject.get_cached_object(bbs_key)
		if(bbs == None):
			Alert.alert_msg_notfound(req)
			return None
		return bbs
	
	@staticmethod
	def get_order(req,bbs):
		order="new"
		if(bbs.default_order==2):
			order="update"
		if(bbs.bbs_mode==BbsConst.BBS_MODE_NO_IMAGE):
			order="update"
		if req.request.get("order"):
			order=req.request.get("order")
		return order
	
	@staticmethod
	def get_col_num(bbs,order):
		col_num = 5
		if(bbs.page_illust_n):
			col_num=bbs.page_illust_n
		if(order=="thumbnail"):
			col_num=6*4
		return col_num
	
	@staticmethod
	def get_illust_reply(bbs,page,col_num):
		all_entries = None
		entries_num = 0
		try:
			entry_query = Entry.all().filter("bbs_key =", bbs)
			entry_query.filter("illust_reply =",1)
			entry_query.filter("del_flag =",1)
			entry_query.order("-date")
			entries_num=entry_query.count()
			all_entries=entry_query.fetch(limit=col_num, offset=(page-1)*col_num)
		except:
			None
		return {"entry":all_entries,"count":entries_num}
		