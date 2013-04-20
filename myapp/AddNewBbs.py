#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#新しい掲示板を作成する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

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

from myapp.Bbs import Bbs
from myapp.Counter import Counter
from myapp.Alert import Alert
from myapp.MappingId import MappingId
from myapp.SyncPut import SyncPut
from myapp.BbsConst import BbsConst

class AddNewBbs(webapp.RequestHandler):
	def post(self):
		if(self.request.get('bbs_title')==""):
			Alert.alert_msg_with_write(self,"タイトルを入力して下さい。");
			return                        
		if(self.request.get('bbs_summary')==""):
			Alert.alert_msg_with_write(self,"概要を入力して下さい。");
			return                        
		user = users.get_current_user()
		summary = self.request.get('bbs_summary')		
		
		if(int(self.request.get('official'))==1):
			Alert.alert_msg_with_write(self,"オフィシャル掲示板は廃止されました。");
			return                        
		
		if (not user):
			if(int(self.request.get('official'))==0):
				self.redirect(str(users.create_login_url("")))
				return
		
		#summary = cgi.escape(summary)
		compiled_line = re.compile("\r\n|\r|\n")
		summary = compiled_line.sub(r'<br>', summary)

		short=self.request.get('short')
		if(MappingId.key_format_check(short)):
			Alert.alert_msg_with_write(self,"IDは半角英数である必要があります。")
			return		
		if(MappingId.check_capability(short,"")==0):
			Alert.alert_msg_with_write(self,"ID:"+short+"は既に登録されています。")
			return
		if(short==""):
			Alert.alert_msg_with_write(self,"IDを入力する必要があります。")
			return
				
		new_bbs = Bbs()
		new_bbs.official=int(self.request.get('official'))
		new_bbs.illust_n=0
		new_bbs.bbs_name = cgi.escape(self.request.get('bbs_title'))
		new_bbs.summary = summary
		new_bbs.owner = user
		new_bbs.user_id = user.user_id()
		new_bbs.bg_color="ffffff"
		new_bbs.font_color="333333"
		new_bbs.background_image=""
		new_bbs.bottom_image=""
		new_bbs.button_color="999999"
		new_bbs.button_active_color="777777"
		new_bbs.bbs_mode=int(self.request.get('mode'))
		new_bbs.my_homepage=""
		new_bbs.del_flag=0
		new_bbs.enable_continue_draw=0
		new_bbs.enable_moper=0
		new_bbs.enable_full_flat=1
		new_bbs.short=short
		new_bbs.delete_when_upload_success=1
		
		new_bbs.applause_n=0
		new_bbs.illust_n=0
		new_bbs.comment_n=0
		
		new_bbs.page_illust_n=5
		new_bbs.page_comment_n=10
		new_bbs.disable_applause=0
		new_bbs.default_order=0
		
		new_bbs.enable_illust_reply=1
		new_bbs.enable_illust_reply_continue=0
		new_bbs.disable_normal_reply=0
		new_bbs.illust_reply_width=400
		new_bbs.illust_reply_height=200
		
		new_bbs.side_color="ffffff"
		new_bbs.side_font_color="333333"
		new_bbs.side_background_image=""
		
		new_bbs.comment_rule_enable=0
		new_bbs.comment_rule=""

		new_bbs.default_canvas_size=0
		new_bbs.default_canvas_width=0
		new_bbs.default_canvas_height=0
		new_bbs.disable_counter=0
		new_bbs.disable_draw_time=0
		new_bbs.disable_portal_menu=0
		new_bbs.in_frame_mode=0;
		new_bbs.spoit_mode=0;
		new_bbs.disable_news=0;
		
		new_bbs.twitter_id=""
		new_bbs.twitter_enable=0
		new_bbs.twitter_bg_color="ffffff"
		new_bbs.twitter_font_color="333333"
		new_bbs.twitter_shell_color="ffffff"
		new_bbs.twitter_height=300
		
		new_bbs.design_template_no=1
		
		new_bbs.content_bg_color="ffffff"
		new_bbs.content_font_color="333333"
		
		new_bbs.content_width=800
		
		new_bbs.enable_full_comment=1

		new_bbs.freearea=""
		new_bbs.amazon=""
		new_bbs.freearea_title=""
		new_bbs.amazon_title=""
		
		new_bbs.create_date=datetime.datetime.today()

		if(memcache.get(BbsConst.OBJECT_NEW_BBS_CREATING_HEADER+short)):
			Alert.alert_msg_with_write(self,"二重投稿を検知しました。戻ってリロードして下さい。")
			return
		memcache.set(BbsConst.OBJECT_NEW_BBS_CREATING_HEADER+short,"creating",BbsConst.NEW_BBS_CACHE_TIME)
		
		counter=Counter()
		counter.init_cnt()
		counter.put()
		new_bbs.counter=counter.key()
		SyncPut.put_sync(new_bbs)

		self.redirect(str(self.request.get('redirect')))

