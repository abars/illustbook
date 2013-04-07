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

from google.appengine.ext.webapp import template
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

class AddEntry(webapp.RequestHandler):
	def post(self):
		entry = Entry()
		if(self.request.get('comment')):
			entry.content = self.request.get('comment')
		else:
			if(self.request.get('image')):
				entry.content = ""
			else:
				Alert.alert_msg_with_write(self,"コメントを入力して下さい。");
				return

		if(not self.request.get('image')):
			if(self.request.get("seed")!=BbsConst.SUBMIT_SEED):
				Alert.alert_msg_with_write(self,"シードが一致しません。");
				return

		if(self.request.get('mail_addr')):
			entry.mail=self.request.get('mail_addr')
		else:
			entry.mail=""
		
		if(self.request.get('homepage_addr') and self.request.get('homepage_addr')!="http://"):
			entry.homepage_addr=self.request.get('homepage_addr')
		else:
			entry.homepage_addr=""

		checkcode=SpamCheck.get_check_code()
		if(SpamCheck.check(entry.content,checkcode)):			
			Alert.alert_msg_with_write(self,BbsConst.SPAM_CHECKED);
			return

		thread=db.Key(self.request.get("thread_key"))
		bbs = db.get(self.request.get("bbs_key"))

		#二重投稿ブロック
		if(entry.content!="" and memcache.get("add_entry_double_block")==entry.content):
			url=MappingThreadId.get_thread_url("./",bbs,db.get(self.request.get("thread_key")))
			self.redirect(str(url))
			return
		
		#コメント禁止
		if(db.get(thread).prohibit_comment):
			Alert.alert_msg_with_write(self,"このイラストへのコメントは禁止されています。");
			return
		
		#書き込み権限確認
		user = users.get_current_user()

		if(bbs.comment_login_require):
			if(not(user)):
				Alert.alert_msg_with_write(self,"この掲示板ではコメントする際にログインが必須です。");
				return
		
		if(self.request.get('image')):
			timage=ThreadImage()
			timage.bbs_key=bbs

			if(self.request.get("base64") and self.request.get("base64")=="1"):
				timage.image=db.Blob(base64.b64decode(self.request.get("image")))
				timage.thumbnail=db.Blob(base64.b64decode(self.request.get("thumbnail")))
			else:
				timage.image=db.Blob(self.request.get("image"))
				timage.thumbnail=db.Blob(self.request.get("thumbnail"))
			timage.illust_mode=1;
			timage.put()

			entry.illust_reply=1
			entry.illust_reply_image_key=timage#str(timage.key())	
		else:
			entry.content=cgi.escape(entry.content)
		
			compiled_line = re.compile("(http://[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)")
			entry.content = compiled_line.sub(r'<a href=\1 TARGET="_blank">\1</a>', entry.content)		

		compiled_line = re.compile("\r\n|\r|\n")
		entry.content = compiled_line.sub(r'<br>', entry.content)

		compiled_line = re.compile("<P>|</P>")
		entry.content = compiled_line.sub(r'', entry.content)
		
		if(self.request.get('author')):
			entry.editor = cgi.escape(self.request.get('author'))
		else:
			entry.editor = "no_name"
			Alert.alert_msg_with_write(self,"名前を入力して下さい。");
			return
			
		entry.thread_key = thread
		entry.bbs_key = bbs
		entry.del_flag = 1
		entry.res_list=[]

		entry.create_date=datetime.datetime.today()
		entry.date=datetime.datetime.today()

		#プロフィールにリンクするか
		link_to_profile=StackFeed.is_link_to_profile(self)
		if(link_to_profile and user):
			entry.user_id=user.user_id()

		#スレッドを取得
		thread = db.get(self.request.get("thread_key"))

		#コメント番号を設定
		entry.comment_no=thread.comment_cnt+1
		entry.remote_addr=self.request.remote_addr

		#保存
		entry.put()

		#スレッドのコメント数を更新
		thread.comment_cnt = thread.comment_cnt+1
		thread.date=datetime.datetime.today()
		thread.cached_entry_key=[]
		thread.cached_entry_key_enable=None
		thread.put()

		#掲示板のコメント数を追加
		if(bbs.comment_n) :
			bbs.comment_n=bbs.comment_n+1
		else:
			bbs.comment_n=1
		bbs.put()
		RecentCommentCache.invalidate(bbs)
		
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
		Ranking.add_rank_global(thread,BbsConst.SCORE_ENTRY)

		#フィード
		if(not link_to_profile):
			user=None
		StackFeed.feed_new_comment_thread(user,thread,entry)
