#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#レスの追加
#

import cgi
import os
import sys
import re
import datetime
import random
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from Bbs import Bbs
from Entry import Entry
from RankingScore import RankingScore
from Response import Response
from MesThread import MesThread
from BbsConst import BbsConst
from ThreadImage import ThreadImage
from SpamCheck import SpamCheck
from Alert import Alert
from OwnerCheck import OwnerCheck
from RecentCommentCache import RecentCommentCache
from MappingId import MappingId
from MappingThreadId import MappingThreadId
from SpamCheck import SpamCheck
from StackFeed import StackFeed

class AddRes(webapp.RequestHandler):
	def post(self):
		entry=None
		try:
			entry = db.get(self.request.get("entry_key"))	
		except:
			entry=None
		if(not entry):
			self.response.out.write(Alert.alert_msg("エントリーが見つかりません。",self.request.host));
			return

		thread_key=entry.thread_key
		bbs_key=thread_key.bbs_key

		#書き込み権限チェック
		user = users.get_current_user()
		if(bbs_key.comment_login_require):
			if(not(user)):
				self.response.out.write(Alert.alert_msg("この掲示板ではコメントする際にログインが必須です。",self.request.host));
				return

		response = Response()
		if(self.request.get('comment')):
			response.content = cgi.escape(self.request.get('comment'))
		else:
			self.response.out.write(Alert.alert_msg("コメントを入力して下さい。",self.request.host));
			return

		#二重投稿ブロック
		if(response.content!="" and memcache.get("add_res_double_block")==response.content):
			url=MappingThreadId.get_thread_url("./",bbs_key,thread_key)
			self.redirect(str(url))
			return

		checkcode=SpamCheck.get_check_code()
		if(SpamCheck.check(response.content,checkcode)):			
			self.response.out.write(Alert.alert_msg(BbsConst.SPAM_CHECKED,self.request.host));
			return
		
		compiled_line = re.compile("\r\n|\r|\n")
		response.content = compiled_line.sub(r'<br>', response.content)
		
		compiled_line = re.compile("(http://[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)")
		response.content = compiled_line.sub(r'<a href=\1 TARGET="_blank">\1</a>', response.content)
		
		if(self.request.get('author')):
			try:
				response.editor = cgi.escape(self.request.get('author'))
			except:
				self.response.out.write(Alert.alert_msg("名前に改行は使用できません。",self.request.host));
				return
		else:
			response.editor = "no_name"
			self.response.out.write(Alert.alert_msg("名前を入力して下さい。",self.request.host));
			return

		if(self.request.get('link_to_profile')=="on"):
			if(user):
				response.user_id=user.user_id()
		
		response.put()
		
		#thread_key
		entry.res_list.append(response.key())
		entry.last_update_editor = response.editor
		entry.date=datetime.datetime.today()
		entry.put()
		
		url=MappingThreadId.get_thread_url("./",bbs_key,thread_key)
		self.redirect(str(url))
		
		thread = thread_key
		thread.comment_cnt = thread.comment_cnt+1
		thread.date=datetime.datetime.today()
		thread.put()

		if(bbs_key.comment_n) :
			bbs_key.comment_n=bbs_key.comment_n+1
		else:
			bbs_key.comment_n=1
		bbs_key.put()

		RecentCommentCache.invalidate(bbs_key)

		#二重投稿ブロック
		memcache.set("add_res_double_block",self.request.get("comment"),30)

		#フィード
		StackFeed.feed_new_response_entry(user,thread,entry)

