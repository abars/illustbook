#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#コメントを投稿する
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
from myapp.MappingId import MappingId
from myapp.MappingThreadId import MappingThreadId
from myapp.StackFeed import StackFeed
from myapp.Ranking import Ranking
from myapp.EscapeComment import EscapeComment
from myapp.SyncPut import SyncPut
from myapp.SetUtf8 import SetUtf8
from myapp.CssDesign import CssDesign

class AddEntry(webapp.RequestHandler):
	def write_status(self,is_flash,msg):
		if(is_flash):
			self.response.headers ['Content-type'] = "text/html;charset=utf-8";
			self.response.out.write(msg);
		else:
			Alert.alert_msg_with_write(self,msg);

	def set_basic_info(self,entry,thread):
		#新規作成時の基本情報を設定
		entry.res_list=[]
		entry.date=datetime.datetime.today()
		entry.create_date=datetime.datetime.today()

		#コメント番号を設定
		entry.comment_no=thread.comment_cnt+1
		entry.remote_addr=self.request.remote_addr
		entry.remote_host=self.request.get("remote_host")

	def update_thread_and_bbs_information(self,thread,bbs,entry):
		#スレッドのコメント数を更新
		thread.comment_cnt = thread.comment_cnt+1
		thread.date=datetime.datetime.today()
		thread.cached_entry_key=[]
		thread.cached_entry_key_enable=None
		if(entry.illust_reply):
			thread.cached_entry_image_key=str(entry.illust_reply_image_key.key())
		thread.put()

		#掲示板のコメント数を追加
		if(bbs.comment_n) :
			bbs.comment_n=bbs.comment_n+1
		else:
			bbs.comment_n=1
		bbs.put()
		RecentCommentCache.invalidate(bbs)

	def post(self):
		SetUtf8.set()
		is_english=CssDesign.is_english(self)

		#エラーコードはFlash向けかどうか
		is_flash=False
		if(self.request.get('image')):
			is_flash=True

		#書き込み対象のコメントを取得
		if(self.request.get("entry_key")):	#上書きモード
			entry = db.get(self.request.get("entry_key"))
			overwrite = True
		else:
			entry = Entry()
			overwrite = False
	
		#コメント
		if(self.request.get('comment')):
			entry.content = self.request.get('comment')
		else:
			if(self.request.get('image')):
				entry.content = ""
			else:
				if(is_english):
					self.write_status(is_flash,"Please input comment");
				else:
					self.write_status(is_flash,"コメントを入力して下さい。");
				return

		#名前
		if(self.request.get('author')):
			entry.editor = cgi.escape(self.request.get('author'))
		else:
			entry.editor = "no_name"
			if(is_english):
				self.write_status(is_flash,"Please input name");
			else:
				self.write_status(is_flash,"名前を入力して下さい。");
			return
			

		if(not self.request.get('image')):
			if(self.request.get("seed")!=BbsConst.SUBMIT_SEED):
				self.write_status(is_flash,"シードが一致しません。");
				return

		if(self.request.get('mail_addr')):
			entry.mail=self.request.get('mail_addr')
		else:
			entry.mail=""
		
		if(self.request.get('homepage_addr') and self.request.get('homepage_addr')!="http://"):
			entry.homepage_addr=self.request.get('homepage_addr')
		else:
			entry.homepage_addr=""

		user = users.get_current_user()

		thread=db.Key(self.request.get("thread_key"))
		bbs = db.get(self.request.get("bbs_key"))

		if(SpamCheck.check_all(self,entry.content,self.request.get("remote_host"),user,bbs,is_flash,is_english)):
			return

		#二重投稿ブロック
		if(entry.content!="" and memcache.get("add_entry_double_block")==entry.content):
			if(is_flash):
				self.write_status(is_flash,"二重投稿を検出しました。時間を置いて、再度、投稿して下さい。");
			else:
				url=MappingThreadId.get_thread_url("./",bbs,db.get(self.request.get("thread_key")))
				self.redirect(str(url))
			return
		
		#コメント禁止
		if(db.get(thread).prohibit_comment):
			self.write_status(is_flash,"このイラストへのコメントは禁止されています。");
			return
		
		#書き込み権限確認
		if(bbs.comment_login_require or BbsConst.FORCE_LOGIN_TO_CREATE_NEW_COMMENT):
			if(not(user)):
				self.write_status(is_flash,"この掲示板ではコメントする際にログインが必須です。");
				return

		#上書き権限確認
		if(overwrite):
			bbs=db.get(self.request.get("bbs_key"))
			if(OwnerCheck.check(bbs,user)):
				if(user and entry.user_id!=user.user_id()):
					self.write_status(is_flash,"上書き投稿する権限がありません。");
					return
		
		#イラストの設定
		delete_thread_image=None
		if(self.request.get('image')):
			if(overwrite):
				delete_thread_image=entry.illust_reply_image_key
			timage=ThreadImage()
			timage.bbs_key=bbs

			if(self.request.get("base64") and self.request.get("base64")=="1"):
				timage.image=db.Blob(base64.b64decode(self.request.get("image")))
				timage.thumbnail=db.Blob(base64.b64decode(self.request.get("thumbnail")))
			else:
				timage.image=db.Blob(self.request.get("image"))
				timage.thumbnail=db.Blob(self.request.get("thumbnail"))
			timage.thumbnail2=None
			timage.illust_mode=1;
			try:
				timage.put()
			except:
				if(is_english):
					self.write_status(is_flash,"Too big image");
				else:
					self.write_status(is_flash,"画像サイズが大きすぎます。");
				return

			entry.illust_reply=1
			entry.illust_reply_image_key=timage
		else:
			entry.content=cgi.escape(entry.content)
			entry.content=EscapeComment.auto_link(entry.content)

		entry.content=EscapeComment.escape_br(entry.content)

		entry.thread_key = thread
		entry.bbs_key = bbs
		entry.del_flag = 1
		if(self.request.get("regulation")):
			entry.adult=int(self.request.get("regulation"))

		#プロフィールにリンクするか
		link_to_profile=StackFeed.is_link_to_profile(self)
		if((link_to_profile or BbsConst.FORCE_LOGIN_TO_CREATE_NEW_COMMENT) and user):
			entry.user_id=user.user_id()

		#スレッドを取得
		thread = db.get(self.request.get("thread_key"))

		#基本情報を設定
		if(not overwrite):
			self.set_basic_info(entry,thread)

		#保存
		if(not SyncPut.put_sync(entry)):
			message="コメントの投稿は成功しましたが表示が遅延しています。反映まで数分お待ちください。"
			memcache.set(BbsConst.OBJECT_THREAD_MESSAGE_HEADER+str(thread.key()),message,BbsConst.OBJECT_THREAD_MESSAGE_CACHE_TIME)
			memcache.set(BbsConst.OBJECT_BBS_MESSAGE_HEADER+str(bbs.key()),message,BbsConst.OBJECT_BBS_MESSAGE_CACHE_TIME)

		#スレッドと掲示板の情報を更新
		if(not overwrite):
			self.update_thread_and_bbs_information(thread,bbs,entry)

		#上書き投稿時の昔のイラストの削除
		if(delete_thread_image):
			delete_thread_image.delete()

		#ステータスコードを出力
		if(self.request.get('image')):
			self.response.headers ['Content-type'] = "text/html;charset=utf-8"  
			self.response.out.write("success")			
		else:
			url=MappingThreadId.get_thread_url("./",bbs,thread)
			if(self.request.get("redirect_url")):
				url=self.request.get("redirect_url")
			self.redirect(str(url))

		#二重投稿ブロック
		memcache.set("add_entry_double_block",self.request.get("comment"),30)
		
		#ランキング
		is_owner=False
		if(thread.user_id and entry.user_id and thread.user_id == entry.user_id):
			is_owner=True
		if(not is_owner): #自分のスレッドへのコメントはランキングに反映しない
			Ranking.add_rank_global(thread,BbsConst.SCORE_ENTRY)

		#フィード
		if(not link_to_profile):
			user=None
		try:
			StackFeed.feed_new_comment_thread(user,thread,entry)
		except:
			logging.error("new entry stackfeed add error")
