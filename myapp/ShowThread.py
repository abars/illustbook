#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドの表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
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
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.ShowBbs import ShowBbs
from myapp.CounterWorker import CounterWorker
from myapp.ApiObject import ApiObject
from myapp.ShowEntry import ShowEntry
from myapp.SearchThread import SearchThread
from myapp.SpamCheck import SpamCheck

class ShowThread(webapp.RequestHandler):
	def get(self,bbs_key,thread_key):
		SetUtf8.set()

		#ホストチェック
		if SpamCheck.is_deny(self.request):
			self.response.set_status(401)
			return

		#英語版かどうか
		is_english=CssDesign.is_english(self)

		#BBSを取得
		bbs_key=MappingId.mapping(bbs_key)
		bbs=ApiObject.get_cached_object(bbs_key)
		if(bbs == None):
			Alert.alert_msg_notfound(self)
			return

		#BBSが削除されていた場合
		if(bbs.del_flag) :
			if(is_english):
				Alert.alert_msg_with_write(self,"This bbs was deleted.")
			else:
				Alert.alert_msg_with_write(self,"このBBSは削除されました。")
			return
		
		#ページ番号を取得
		col_num = 10
		page = 1
		if self.request.get("page"):
			page = int(self.request.get("page"))
			if page < 1:
				page=1
		
		#メンテナンス画面
		is_maintenance=0
		if(MaintenanceCheck.is_appengine_maintenance()):
			is_maintenance=1

		#オーダー取得
		order="update"
		if(bbs.default_comment_order==1):
			order="new"
		if self.request.get("order"):
			order=self.request.get("order")
		
		#スレッド取得
		thread=ShowThread.get_thread(bbs,thread_key)
		if(thread == None):
			Alert.alert_msg_notfound(self)
			return

		#コメント数を更新
		if(bbs.page_comment_n):
			col_num=bbs.page_comment_n
		if(self.request.get("limit")):
			col_num=int(self.request.get("limit"))

		#コメントの一覧を取得
		query=ShowThread.get_comment_query(thread,order)
		entry_num = query.count()
		if(entry_num==0):
			com_list_ = []
		else:
			com_list_ = query.fetch(limit=col_num, offset=(page-1)*col_num)
		
		#検索
		search=""
		if(self.request.get("search")):
			search=self.request.get("search")
			query=""+search+' thread_key:"'+str(thread.key())+'"'
			com_list_=SearchThread.search(query,page,col_num,BbsConst.SEARCH_ENTRY_INDEX_NAME)
		
		#実体への変換
		com_list_=ApiObject.get_cached_object_list(com_list_)

		#現在のスレッドへのURLを取得
		host_url=MappingId.mapping_host_with_scheme(self.request)+"/"
		
		#編集モードか
		user = users.get_current_user()
		edit_flag = 0
		if(not OwnerCheck.check(bbs,user)):
			edit_flag = 1

		logined=0
		if(user):
			logined=1

		owner=user
		if(OwnerCheck.check(bbs,user)):
			owner=None

		admin_user=OwnerCheck.is_admin(user)

		#ページリンクを作成
		page_url_base = MappingId.get_usr_url(host_url,bbs)+thread_key+'.html?page='
		page_list=ShowThread.create_page_list(page,entry_num,col_num)
		
		#掲示板のデザインを取得
		design=CssDesign.get_design_object(self,bbs,host_url,1)

		#コメントフォームを取得する
		show_comment_form=1
		if(bbs.comment_login_require and not(owner)):
			show_comment_form=0
		
		#名前取得
		user_name=ShowEntry.get_user_name(user)
		
		#自分のイラストか
		my_illust=False
		if(user and thread.user_id==user.user_id()):
			my_illust=True

		#IPを表示するかどうか
		show_ip=False
		if(self.request.get("show_ip") and (owner or admin_user)):
			show_ip=True

		#コメントのレンダリング
		comment=ShowEntry.render_comment(self,host_url,bbs,thread,com_list_,edit_flag,bbs_key,logined,show_comment_form,admin_user,user_name,user,show_ip)
		
		#凍結されているか
		frozen=ApiObject.is_frozen_thread(thread)

		#拍手が有効かどうか
		applause_enable=not (user and thread.user_id and thread.user_id==user.user_id())

		#メッセージ
		message=memcache.get(BbsConst.OBJECT_THREAD_MESSAGE_HEADER+str(thread.key()))

		#関連イラスト
		related=self._get_related(bbs,thread,design["is_iphone"],design["is_tablet"])

		#スパム対策
		force_login_to_create_new_image=BbsConst.FORCE_LOGIN_TO_CREATE_NEW_IMAGE
		force_login_to_create_new_comment=BbsConst.FORCE_LOGIN_TO_CREATE_NEW_COMMENT

		#描画
		template_values = {
			'host': host_url,
			'usrhost': MappingId.get_usr_url(host_url,bbs),
			'bbs': bbs,
			'bbs_str_key': str(bbs.key()),
			'thread': thread,
			'edit_flag':edit_flag,
			'url': 'edit',
			'url_linktext': 'edit blogs',
			'bbs_key': bbs_key,
			'page':page,
			'page_url_base':page_url_base,
			'page_list':page_list,
			'logined':logined,
			'user':user,
			'owner':owner,
			'my_illust':my_illust,
			'template_path':design["template_path"],
			'css_name':design["css_name"],
			'is_iphone':design["is_iphone"],
			'is_tablet':design["is_tablet"],
			'template_base_color':design["template_base_color"],
			'admin_user':admin_user,
			'order':order,
			'is_maintenance':is_maintenance,
			'redirect_url': self.request.path,
			'comment':comment,
			'show_comment_form':show_comment_form,
			'user_name':user_name,
			'search': search,
			'limit': col_num,
			'frozen': frozen,
			'applause_enable': applause_enable,
			'message': message,
			'is_english': is_english,
			'related': related,
			'show_ip': show_ip,
			'force_login_to_create_new_image': force_login_to_create_new_image,
			'force_login_to_create_new_comment': force_login_to_create_new_comment
			}

		path = "/html/"+design["base_name"]
		self.response.out.write(template_select.render(path, template_values))

		CounterWorker.update_counter(self,bbs,thread,owner)

	@staticmethod
	def _get_related_query(bbs,thread):
		thread_query = db.Query(MesThread,keys_only=True)
		if(thread.user_id):
			thread_query.filter('user_id =',thread.user_id)
		thread_query.filter('bbs_key =', bbs)
		thread_query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		return thread_query

	@staticmethod
	def _get_related(bbs,thread,is_iphone,is_tablet):
		related_illust_cnt=6

		try:
			thread_query=ShowThread._get_related_query(bbs,thread)
			thread_query.filter('create_date > ',thread.create_date)
			thread_query.order('create_date')
			thread_after=thread_query.fetch(limit=related_illust_cnt)
		except:
			thread_after=[]

		try:
			thread_query=ShowThread._get_related_query(bbs,thread)
			thread_query.filter('create_date < ',thread.create_date)
			thread_query.order('-create_date')
			thread_before=thread_query.fetch(limit=related_illust_cnt*2-len(thread_after))
		except:
			thread_before=[]

		all_threads=[]
		if(thread_after):
			thread_after.reverse()

		for after in thread_after:
			all_threads.append(after)
		for before in thread_before:
			all_threads.append(before)

		if(not is_iphone and not is_tablet):
			while(len(all_threads)>related_illust_cnt+1):
				no=int(random.random()*len(all_threads))
				all_threads.remove(all_threads[no])

		all_threads_cached=ApiObject.get_cached_object_list(all_threads)
		return all_threads_cached

	@staticmethod
	def get_thread(bbs,thread_key):
		thread = MappingThreadId.mapping(bbs,thread_key)
		if(thread == None):
			return None
		
		MappingThreadId.assign(bbs,thread,True)
		return thread
	
	@staticmethod
	def create_page_list(page,entry_num,col_num):
		page_start = page-2
		if(page_start <= 0):
			page_start = 1
		page_end=page_start+4
		max_page=(entry_num-1)/col_num+1
		if(not max_page):
			max_page=1
		if(page_end > max_page):
			page_end=max_page
			if(page_end-4 >= 1):
				page_start=page_end-4
		page_list=range(page_start, (page_end+1))
		return page_list
	
	@staticmethod
	def get_comment_query(thread,order):
		#query = Entry.all()
		query=db.Query(Entry,keys_only=True)
		query.filter('thread_key =', thread)
		query.filter("del_flag =",1)
		if(order=="new"):
			query.order('-create_date')
		else:
			query.order('-date')
		return query




