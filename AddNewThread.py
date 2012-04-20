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

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from Bbs import Bbs
from Entry import Entry
from Response import Response
from MesThread import MesThread
from BbsConst import BbsConst
from ThreadImage import ThreadImage
from SpamCheck import SpamCheck
from Alert import Alert
from OwnerCheck import OwnerCheck
from RecentCommentCache import RecentCommentCache
from ImageFile import ImageFile
from MappingThreadId import MappingThreadId
from Bookmark import Bookmark

from UTC import UTC
from JST import JST

from StackFeed import StackFeed
from SyncPut import SyncPut

class AddNewThread(webapp.RequestHandler):
	def post(self):
		if(self.request.get('thread_title')==""):
			self.response.out.write(Alert.alert_msg("スレッドタイトルを入力して下さい。",self.request.host));
			return                        
		if(self.request.get('author')==""):
			self.response.out.write(Alert.alert_msg("投稿者名を入力して下さい。",self.request.host));
			return                        
		bbs = db.get(self.request.get("bbs_key"))
		user = users.get_current_user()
		if(bbs.bbs_mode==BbsConst.BBS_MODE_ONLY_ADMIN):
			if(OwnerCheck.check(bbs,user)):
				self.response.out.write(Alert.alert_msg("スレッドを作成する権限がありません。",self.request.host));
				return
		if(bbs.bbs_mode==BbsConst.BBS_MODE_NO_IMAGE):
			if(bbs.disable_create_new_thread==1):
				if(OwnerCheck.check(bbs,user)):
					self.response.out.write(Alert.alert_msg("スレッドを作成する権限がありません。",self.request.host));
					return
			if(bbs.disable_create_new_thread==2):
				if(not user):
					self.response.out.write(Alert.alert_msg("スレッドを作成する権限がありません。",self.request.host));
					return

		checkcode=SpamCheck.get_check_code()
		if(SpamCheck.check(self.request.get('thread_title'),checkcode)):
			self.response.out.write(Alert.alert_msg(BbsConst.SPAM_CHECKED,self.request.host));
			return

		homepage_addr=""
		if(self.request.get('homepage_addr') and self.request.get('homepage_addr')!="http://"):
			homepage_addr=self.request.get('homepage_addr')
		
		if(self.request.get("thread_key")):	#上書きモード
			#上書きの場合
			new_thread=db.get(self.request.get("thread_key"))
			if(OwnerCheck.check(bbs,user)):
				if(self.request.get("delete_key")!=new_thread.delete_key or new_thread.delete_key==""):
					self.response.out.write(Alert.alert_msg("上書きをする権限がありません。",self.request.host));
					return;
		else:
			#新規作成の場合
			new_thread = MesThread()
			new_thread.put()	#キーの確保
			
			new_thread.score = None
			
			new_thread.comment_cnt=0

			bbs.illust_n=bbs.illust_n+1
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

		compiled_line = re.compile("\r\n|\r|\n")
		new_thread.summary = compiled_line.sub(r'<br>', new_thread.summary)

		compiled_line = re.compile("<P>|</P>")
		new_thread.summary = compiled_line.sub(r'', new_thread.summary)
				
		new_thread.homepage_addr=homepage_addr
		new_thread.author=self.request.get('author')
		if(self.request.get("draw_time")):
			new_thread.draw_time=int(self.request.get("draw_time")	)			
		if(self.request.get("delete_key")):
			new_thread.delete_key=self.request.get("delete_key")

		if(self.request.get("category")):
			new_thread.category=self.request.get("category")
		
		if(self.request.get("is_png")):
			new_thread.is_png=1
		else:
			new_thread.is_png=0
		
		if(self.request.get("link_to_profile")):
			if(self.request.get("link_to_profile")=="on" and user):
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
		if(self.request.get('mode')=="illust_all" and new_thread.illust_mode!=BbsConst.ILLUSTMODE_TEXT):
			timage=ThreadImage()
			timage.bbs_key=db.get(self.request.get("bbs_key"))
			
			if(self.request.get("base64") and self.request.get("base64")=="1"):
				timage.image=db.Blob(base64.b64decode(self.request.get("image")))
				timage.thumbnail=db.Blob(base64.b64decode(self.request.get("thumbnail")))
			else:
				timage.image=db.Blob(self.request.get("image"))
				timage.thumbnail=db.Blob(self.request.get("thumbnail"))
			
			if(len(timage.image)<=0 or len(timage.thumbnail)<=0):
				self.response.out.write(Alert.alert_msg("画像データが不正です。",self.request.host));
				return

			timage.illust_mode=new_thread.illust_mode
			timage.is_png=new_thread.is_png
			timage.put()
			new_thread.image_key=timage#db.Key(str(timage.key()))
			ImageFile.invalidate_cache(str(timage.key()))

		#url assign
		MappingThreadId.assign(bbs,new_thread,False)
		
		#put
		#new_thread.put()
		SyncPut.put_sync(new_thread)
	
		#ステータスを出力
		if(self.request.get('mode')=="illust" or self.request.get('mode')=="illust_all"):
			self.response.headers ['Content-type'] = "text/html;charset=utf-8"  
			self.response.out.write("success")
		else:
			self.redirect(str('./bbs_index?bbs_key='+self.request.get('bbs_key')))
		
		#tweet
		url=self.get_thread_url(bbs,new_thread)
		StackFeed.feed_new_thread(user,bbs,new_thread)
		#self.tweet(bbs,new_thread,url)
	
	def get_thread_url(self,bbs,new_thread):
		#thread info
		url="http://"+self.request.host+"/"
		#www.illustbook.net/";
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
	
	#def tweet(self,bbs,new_thread,url):
		#tweet
	#	try:
	#		if(not bbs.disable_news and not self.request.get("thread_key")):
	#			if(new_thread.illust_mode==1 or new_thread.illust_mode==2):
	#				footer=""
	#				tweet=""+bbs.bbs_name+"に"+new_thread.title+"が投稿されたよ！"+footer	
	#				if(self.request.host == "www.illustbook.net" or self.request.host == "illust-book.appspot.com"):
	#					TweetRss.tweet(tweet,url);
	#				else:
	#					logging.getLogger().setLevel(logging.DEBUG)
	#					logging.debug(tweet)
	#	except:
	#		tweet_error_disable=1
