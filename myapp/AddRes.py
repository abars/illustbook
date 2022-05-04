#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#新規レスの作成
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
from myapp.SpamCheck import SpamCheck
from myapp.StackFeed import StackFeed
from myapp.Ranking import Ranking
from myapp.EscapeComment import EscapeComment
from myapp.SetUtf8 import SetUtf8
from myapp.CssDesign import CssDesign

class AddRes(webapp.RequestHandler):
	def write_status(self,is_flash,msg):
		if(is_flash):
			self.response.headers ['Content-type'] = "text/html;charset=utf-8";
			self.response.out.write(msg);
		else:
			Alert.alert_msg_with_write(self,msg);

	def post(self):
		SetUtf8.set()
		is_english=CssDesign.is_english(self)

		entry=None
		try:
			entry = db.get(self.request.get("entry_key"))
		except:
			entry=None
		if(not entry):
			Alert.alert_msg_with_write(self,"エントリーが見つかりません。");
			return

		thread_key=entry.thread_key
		bbs_key=thread_key.bbs_key

		#スパムチェック
		if(self.request.get("seed")!=BbsConst.SUBMIT_SEED):
			Alert.alert_msg_with_write(self,"シードが一致しません。");
			return

		#コメント禁止
		if(thread_key.prohibit_comment):
			Alert.alert_msg_with_write(self,"このイラストへのコメントは禁止されています。");
			return

		#書き込み権限チェック
		user = users.get_current_user()
		if(bbs_key.comment_login_require or BbsConst.FORCE_LOGIN_TO_CREATE_NEW_COMMENT):
			if(not(user)):
				Alert.alert_msg_with_write(self,"この掲示板ではコメントする際にログインが必須です。");
				return

		response = Response()
		if(self.request.get('comment')):
			response.content = cgi.escape(self.request.get('comment'))
		else:
			Alert.alert_msg_with_write(self,"コメントを入力して下さい。");
			return

		#二重投稿ブロック
		if(response.content!="" and memcache.get("add_res_double_block")==response.content):
			url=MappingThreadId.get_thread_url("./",bbs_key,thread_key)
			self.redirect(str(url))
			return

		is_flash=False
		if(SpamCheck.check_all(self,response.content,self.request.get("remote_host"),user,bbs_key,is_flash,is_english)):
			return

		response.content=EscapeComment.escape_br(response.content)
		response.content=EscapeComment.auto_link(response.content)
		
		if(self.request.get('author')):
			try:
				response.editor = cgi.escape(self.request.get('author'))
			except:
				Alert.alert_msg_with_write(self,"名前に改行は使用できません。");
				return
		else:
			response.editor = "no_name"
			if(is_english):
				Alert.alert_msg_with_write(self,"Please input name");
			else:
				Alert.alert_msg_with_write(self,"名前を入力して下さい。");
			return

		#プロフィールにリンクするか
		link_to_profile=StackFeed.is_link_to_profile(self)
		if((link_to_profile or BbsConst.FORCE_LOGIN_TO_CREATE_NEW_COMMENT) and user):
			response.user_id=user.user_id()

		#コメント番号を設定
		response.comment_no=thread_key.comment_cnt+1
		response.remote_addr=self.request.remote_addr
		response.remote_host=self.request.get("remote_host")

		#レスを書き込み
		response.put()
		
		#レスをコメントに追加
		entry.res_list.append(response.key())
		entry.last_update_editor = response.editor
		entry.date=datetime.datetime.today()
		entry.search_index_version=0
		entry.put()
		
		#スレッドのコメント数を更新
		thread = thread_key
		thread.comment_cnt = thread.comment_cnt+1
		thread.date=datetime.datetime.today()
		thread.put()

		#コメント数を更新
		if(bbs_key.comment_n) :
			bbs_key.comment_n=bbs_key.comment_n+1
		else:
			bbs_key.comment_n=1
		bbs_key.put()
		RecentCommentCache.invalidate(bbs_key)

		#ステータス出力
		url=MappingThreadId.get_thread_url("./",bbs_key,thread_key)
		if(self.request.get("redirect_url")):
			url=self.request.get("redirect_url")
		self.redirect(str(url))

		#二重投稿ブロック
		memcache.set("add_res_double_block",self.request.get("comment"),30)

		#ランキング
		Ranking.add_rank_global(thread,BbsConst.SCORE_RES)

		#フィード
		if(not link_to_profile):
			user=None
		try:
			StackFeed.feed_new_response_entry(user,thread,entry,response)
		except:
			logging.error("new res stack feed add error")

