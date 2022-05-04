#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#新規スレッドを作成
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging
import base64

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Entry import Entry
from myapp.Response import Response
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.ThreadImage import ThreadImage
from myapp.SpamCheck import SpamCheck
from myapp.Alert import Alert
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.ImageFile import ImageFile
from myapp.MappingId import MappingId
from myapp.MappingThreadId import MappingThreadId
from myapp.Bookmark import Bookmark
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.StackFeed import StackFeed
from myapp.SyncPut import SyncPut
from myapp.ApiFeed import ApiFeed
from myapp.CategoryList import CategoryList
from myapp.EscapeComment import EscapeComment
from myapp.RssFeed import RssFeed
from myapp.ApiUser import ApiUser
from myapp.CssDesign import CssDesign

class AddNewThread(webapp.RequestHandler):
	def write_status(self,is_flash,msg):
		if(is_flash):
			self.response.headers ['Content-type'] = "text/html;charset=utf-8";
			self.response.out.write(msg);
		else:
			Alert.alert_msg_with_write(self,msg);

	def post(self):
		is_flash=self.request.get('mode')=="illust" or self.request.get('mode')=="illust_all";
		is_english=CssDesign.is_english(self)

		if(self.request.get('thread_title')==""):
			if(is_english):
				self.write_status(is_flash,"Please input title");
			else:
				self.write_status(is_flash,"スレッドタイトルを入力して下さい。");
			return                        
		if(self.request.get('author')==""):
			if(is_english):
				self.write_status(is_flash,"Please input author");
			else:
				self.write_status(is_flash,"投稿者名を入力して下さい。");
			return

		permission_error_str="スレッドを作成する権限がありません。"
		if(is_english):
			permission_error_str="Permission denied"

		login_require="ログインが必要です。"
		if(is_english):
			login_require="Login require"

		bbs = db.get(self.request.get("bbs_key"))
		user = users.get_current_user()

		if(not user and BbsConst.FORCE_LOGIN_TO_CREATE_NEW_IMAGE):
			self.write_status(is_flash,login_require);
			return
		
		delete_key_require="削除キーが必要です。"
		if(is_english):
			delete_key_require="Delete key require"

		if(not user and not self.request.get("delete_key")):
			self.write_status(is_flash,delete_key_require);
			return

		if(bbs.bbs_mode==BbsConst.BBS_MODE_ONLY_ADMIN):
			if(OwnerCheck.check(bbs,user)):
				self.write_status(is_flash,permission_error_str);
				return
		if(bbs.bbs_mode==BbsConst.BBS_MODE_NO_IMAGE):
			if(bbs.disable_create_new_thread==1):
				if(OwnerCheck.check(bbs,user)):
					self.write_status(is_flash,permission_error_str);
					return
			if(bbs.disable_create_new_thread==2):
				if(not user):
					self.write_status(is_flash,permission_error_str);
					return

		if(SpamCheck.check_all(self,self.request.get('thread_title'),self.request.get("remote_host"),user,bbs,is_flash,is_english)):
			return

		homepage_addr=""
		if(self.request.get('homepage_addr') and self.request.get('homepage_addr')!="http://"):
			homepage_addr=self.request.get('homepage_addr')
		
		overwrite_mode=False
		if(self.request.get("thread_key")):	#上書きモード
			#上書きの場合
			overwrite_mode=True
			new_thread=db.get(self.request.get("thread_key"))
			if(OwnerCheck.check(bbs,user)):
				if((not user) or (not new_thread.user_id) or new_thread.user_id!=user.user_id()):
					if(self.request.get("delete_key")!=new_thread.delete_key or new_thread.delete_key==""):
						self.write_status(is_flash,"上書きをする権限がありません。");
						return;
		else:
			#新規作成の場合
			new_thread = MesThread()
			new_thread.put()	#キーの確保
			
			new_thread.score = None
			
			new_thread.comment_cnt=0

			bbs.illust_n=bbs.illust_n+1
			bbs.cached_threads_num=None	#キャッシュ更新リクエスト
			bbs.put()
			
			#上書きモードの場合は作成日を更新しない
			new_thread.create_date=datetime.datetime.today()
		
		#更新日は更新する
		new_thread.date=datetime.datetime.today()
		
		#各種設定値を書き込み
		new_thread.illust_mode = int(self.request.get('illust_mode'))
		new_thread.title = cgi.escape(self.request.get('thread_title'))
		if(self.request.get('mode')=="illust_all"):
			new_thread.summary = self.request.get('comment')
		else:
			new_thread.summary = cgi.escape(self.request.get('comment'))
		new_thread.bbs_key = db.Key(self.request.get('bbs_key'))

		new_thread.summary=EscapeComment.escape_br(new_thread.summary)

		new_thread.homepage_addr=homepage_addr
		new_thread.author=self.request.get('author')
		if(self.request.get("draw_time")):
			new_thread.draw_time=int(self.request.get("draw_time"))
		if(self.request.get("delete_key")):
			new_thread.delete_key=self.request.get("delete_key")

		if(self.request.get("category")):
			new_thread.category=self.request.get("category")
			CategoryList.add_new_category(bbs,new_thread.category)

		if(self.request.get("event_id")):
			new_thread.event_id=self.request.get("event_id")

		if(self.request.get("regulation")):
			new_thread.adult=int(self.request.get("regulation"))

		if(self.request.get("dont_show_in_portal")):
			new_thread.violate_photo=1

		if(self.request.get("is_png")):
			new_thread.is_png=1
		else:
			new_thread.is_png=0
		
		#プロフィールにリンクするか
		link_to_profile=StackFeed.is_link_to_profile(self)
		if((link_to_profile or BbsConst.FORCE_LOGIN_TO_CREATE_NEW_IMAGE) and user):
			new_thread.user_id=user.user_id()
		
		#通常投稿モード(MOPER)
		if(self.request.get('mode')=="illust"):
			new_thread.image_key=db.get(self.request.get('thread_image'))
			new_thread.mail=self.request.get('thread_mail')

			compiled_line = re.compile("(http://[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)")
			new_thread.summary = compiled_line.sub(r'<a href=\1 TARGET="_blank">\1</a>', new_thread.summary)

			if(user):
				new_thread.user_id=user.user_id()	#必ずプロフィールにマップ

		#一括投稿モード（新エディタ）
		timage=None
		if((self.request.get('mode')=="illust_all" or self.request.get('mode')=="illust_temp") and new_thread.illust_mode!=BbsConst.ILLUSTMODE_TEXT):
			timage=ThreadImage()
			timage.bbs_key=db.get(self.request.get("bbs_key"))
			
			if(self.request.get('mode')=="illust_temp"):
				try:
					temp_image=db.get(self.request.get("temp_illust_key"))
				except:
					temp_image=None
				if(not temp_image):
					self.write_status(is_flash,"画像データが見つかりません。")
					return
				timage.image=temp_image.image
				timage.thumbnail=temp_image.thumbnail
			else:
				if(self.request.get("base64") and self.request.get("base64")=="1"):
					timage.image=db.Blob(base64.b64decode(self.request.get("image")))
					timage.thumbnail=db.Blob(base64.b64decode(self.request.get("thumbnail")))
					new_thread.is_ipad=1
				else:
					timage.image=db.Blob(self.request.get("image"))
					timage.thumbnail=db.Blob(self.request.get("thumbnail"))
			
			if(len(timage.image)<=0 or len(timage.thumbnail)<=0):
				self.write_status(is_flash,"画像データが不正です。");
				return

			timage.illust_mode=new_thread.illust_mode
			timage.is_png=new_thread.is_png
			timage.thumbnail2=None

			try:
				timage.put()
			except:
				if(is_english):
					self.write_status(is_flash,"Too big image");
				else:
					self.write_status(is_flash,"画像の容量が大きすぎます。");
				return
			new_thread.image_key=timage
			ImageFile.invalidate_cache(str(timage.key()))

		#url assign
		MappingThreadId.assign(bbs,new_thread,False)
		
		#IPアドレスを書き込み
		new_thread.remote_addr=self.request.remote_addr
		new_thread.remote_host=self.request.get("remote_host")
		new_thread.thumbnail2_version=0
		new_thread.search_index_version=0

		#put
		if(not SyncPut.put_sync(new_thread)):
			message="イラストの投稿は成功しましたが表示が遅延しています。反映まで数分お待ちください。"
			memcache.set(BbsConst.OBJECT_BBS_MESSAGE_HEADER+str(bbs.key()),message,BbsConst.OBJECT_BBS_MESSAGE_CACHE_TIME)

		#サムネイル更新
		if(timage):
			if(new_thread.adult==0):
				bbs.cached_thumbnail_key=str(timage.key())
				bbs.put()

		#新着イラストのキャッシュ無効化
		RecentCommentCache.invalidate(bbs)
		
		#ステータスを出力
		if(is_flash):
			self.write_status(is_flash,"success")
		else:
			self.redirect(str('./bbs_index?bbs_key='+self.request.get('bbs_key')))
		
		#feed
		if(not link_to_profile):
			user=None
		url=self.get_thread_url(bbs,new_thread)

		if(not overwrite_mode):
			try:
				StackFeed.feed_new_thread(user,bbs,new_thread)
			except:
				logging.error("new thread stack feed add error")

		#submit thread count
		if(user):
			ApiUser.invalidate_thread_count(user.user_id())
		
		#news
		ApiFeed.invalidate_cache()

		#Rss
		RssFeed.invalidate_cache(str(bbs.key()))
	
	def get_thread_url(self,bbs,new_thread):
		url=MappingId.mapping_host_with_scheme(self.request)+"/"
		if(bbs.short):
			url=url+bbs.short+"/";
		else:
			url=url+"usr/"+str(bbs.key())+"/";
		if(new_thread.short):
			url+=new_thread.short
		else:
			url+=str(new_thread.key())
		url+=".html"
		return url
