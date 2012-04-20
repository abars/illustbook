#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#掲示板の表示

import cgi
import os
import sys
import re
import datetime
import random
import logging
import urllib

from google.appengine.api.labs import taskqueue

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from Bbs import Bbs
from Counter import Counter
from Alert import Alert
from MappingId import MappingId
from SetUtf8 import SetUtf8
from OwnerCheck import OwnerCheck
from MaintenanceCheck import MaintenanceCheck
from BbsConst import BbsConst
from MesThread import MesThread
from PageGenerate import PageGenerate
from RecentCommentCache import RecentCommentCache
from Analyze import Analyze
from Entry import Entry
from CssDesign import CssDesign
from ApiObject import ApiObject
from CounterWorker import CounterWorker

class ShowBbs(webapp.RequestHandler):
	def get(self,bbs_key):
		#日本語対応
		SetUtf8.set()
		
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
			self.response.out.write(Alert.alert_msg("この掲示板は削除されました。",self.request.host))
			return

		#ページ取得
		page = 1
		if self.request.get("page"):
			page = int(self.request.get("page"))

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
		threads_num = thread_query.count()
		all_threads = thread_query.fetch(limit=col_num, offset=(page-1)*col_num)
		
		#返信イラストを取得
		all_entries = None
		if(order=="thumbnail"):
			all_entries=ShowBbs.get_illust_reply(bbs,page,col_num,threads_num)
			if(threads_num<all_entries["count"]):
				threads_num=all_entries["count"]
			all_entries=all_entries["entry"]
		
		#ホストURLを取得
		host_url="http://"+MappingId.mapping_host(self.request.host)+"/";
		
		#URLを作成
		mapped_category=urllib.quote(category.encode('utf-8'))
		page_url=MappingId.get_usr_url(host_url,bbs)
		page_url_base=MappingId.get_usr_url(host_url,bbs)+'?order='+order+'&category='+mapped_category+'&page='
		page_url_order_base=MappingId.get_usr_url(host_url,bbs)+'?page=1&category='+mapped_category+'&order='
		page_url_category_base=MappingId.get_usr_url(host_url,bbs)+'?page=1&order='+order+"&category="

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
		
		#カテゴリ一覧を取得
		category_list=None
		if(bbs.category_list):
			if(bbs.category_list!=""):
				category_list=bbs.category_list.split(",")

		#ページデザインを取得
		css_key=self.request.get("css_key")
		design=CssDesign.get_design_object(self,bbs,host_url,0)

		#サイドバー一覧を作成
		sidebar_list=ShowBbs.get_sidebar(bbs,category_list,side_comment)

		#新規スレッドを作成できるか
		can_create_thread=ShowBbs.get_can_create_thread(bbs,user,logined)
		can_create_new_image=ShowBbs.get_can_create_new_image(bbs,owner)

		#スレッドを全て取得
		all_threads_cached=ApiObject.get_cached_object_list(all_threads)

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
			'logined':logined,
			'can_create_thread':can_create_thread,
			'category_list':category_list,
			'page_url_category_base':page_url_category_base,
			'now_category':category,
			'can_create_new_image':can_create_new_image,
			'template_path':design["template_path"],
			'css_name':design["css_name"],
			'is_iphone':design["is_iphone"],
			'template_base_color':design["template_base_color"],
			'sidebar_list': sidebar_list,
			'is_maintenance': is_maintenance,
			'css_key': css_key,
			'redirect_url': self.request.path
		}

		path = os.path.join(os.path.dirname(__file__), "html/"+design["base_name"])
		self.response.out.write(template.render(path, template_values))
		
		if(is_maintenance):
			return
		
		CounterWorker.update_counter(self,bbs,None,owner)

	@staticmethod
	def get_sidebar(bbs,category_list,side_comment):
		sidebar_list=[]
		if(bbs.freearea):
			sidebar_list.append("free")
		if(category_list):
			sidebar_list.append("category")
		if(bbs.amazon):
			sidebar_list.append("affiliate")
		if(side_comment):
			sidebar_list.append("comment")
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
			req.response.out.write(Alert.alert_msg_notfound(req.request.host))
			return None
		bbs=ApiObject.get_cached_object(bbs_key)
		if(bbs == None):
			req.response.out.write(Alert.alert_msg_notfound(req.request.host))
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
	def get_illust_reply(bbs,page,col_num,threads_num):
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
		