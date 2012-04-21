#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板の基本情報を更新
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

from Bbs import Bbs
from Entry import Entry
from Response import Response
from MesThread import MesThread
from BbsConst import BbsConst
from ThreadImage import ThreadImage
from SpamCheck import SpamCheck
from Alert import Alert
from OwnerCheck import OwnerCheck
from MappingId import MappingId
from RecentCommentCache import RecentCommentCache
from AppPortal import AppPortal

class UpdateBbs(webapp.RequestHandler):
	def post(self):
		bbs_key=self.request.get("bbs_key")
		short=self.request.get('short')
		if(MappingId.key_format_check(short)):
			self.response.out.write(Alert.alert_msg("IDは半角英数である必要があります。",self.request.host))
			return
		if(MappingId.check_capability(short,bbs_key)==0):
			self.response.out.write(Alert.alert_msg("ID:"+short+"は既に登録されています。",self.request.host))
			return
		bbs=db.get(bbs_key);
		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			return
		summary = self.request.get('bbs_summary')
		bg_color=self.request.get('bg_color')
		font_color=self.request.get('font_color')
		content_bg_color=self.request.get('content_bg_color')
		content_font_color=self.request.get('content_font_color')
		menu_bg_color=self.request.get('menu_bg_color')
		menu_font_color=self.request.get('menu_font_color')
		side_color=self.request.get('side_color')
		side_font_color=self.request.get('side_font_color')
		twitter_bg_color=self.request.get('twitter_bg_color')
		twitter_font_color=self.request.get('twitter_font_color')
		twitter_shell_color=self.request.get('twitter_shell_color')

		if(menu_bg_color=="None"):
			menu_bg_color="ffffff";		
		if(menu_font_color=="None"):
			menu_font_color="333333";		
		if(content_bg_color=="None"):
			content_bg_color="ffffff";		
		if(content_font_color=="None"):
			content_font_color="333333";		

		if(side_color=="None"):
			side_color="ffffff";		
		if(side_font_color=="None"):
			side_font_color="333333";		
		if(twitter_bg_color=="None"):
			twitter_bg_color="ffffff";		
		if(twitter_font_color=="None"):
			twitter_font_color="333333";		
		if(twitter_shell_color=="None"):
			twitter_shell_color="ffffff";		
		if re.match('[0-9a-fA-F]{1,6}', bg_color) == None:
			error_str="bg_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return
		if re.match('[0-9a-fA-F]{1,6}', font_color) == None:
			error_str="font_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return
		if re.match('[0-9a-fA-F]{1,6}', twitter_bg_color) == None:
			error_str="twitter_bg_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return
		if re.match('[0-9a-fA-F]{1,6}', twitter_font_color) == None:
			error_str="twitter_font_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return
		if re.match('[0-9a-fA-F]{1,6}', side_color) == None:
			error_str="side_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return
		if re.match('[0-9a-fA-F]{1,6}', side_font_color) == None:
			error_str="side_font_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return

		if re.match('[0-9a-fA-F]{1,6}', content_bg_color) == None:
			error_str="content_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return
		if re.match('[0-9a-fA-F]{1,6}', content_font_color) == None:
			error_str="content_font_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return

		if re.match('[0-9a-fA-F]{1,6}', menu_bg_color) == None:
			error_str="menu_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return
		if re.match('[0-9a-fA-F]{1,6}', menu_font_color) == None:
			error_str="menu_font_color is invalid"
			self.redirect(str('./edit_bbs?bbs_key='+self.request.get("bbs_key")+'&error_str='+error_str))
			return
			
		if self.request.get('title'):
			bbs.bbs_name=self.request.get('title')
		bbs.my_homepage=self.request.get('my_homepage')
		bbs.background_image=self.request.get('background_image')
		bbs.side_background_image=self.request.get('side_background_image')
		bbs.bottom_image=self.request.get('bottom_image')
		if(bbs.background_image=="None"):
			bbs.background_image=""
		if(bbs.side_background_image=="None"):
			bbs.side_background_image=""
		if(bbs.bottom_image=="None"):
			bbs.bottom_image=""
		bbs.short=short
		if(bbs.short=="None"):
			bbs.short=""
		MappingId.invalidate(short)

		try:
			if(self.request.get('default_canvas_width')=="None"):
				bbs.default_canvas_width=0
			else:
				bbs.default_canvas_width=int(self.request.get('default_canvas_width'))
			if(self.request.get('default_canvas_height')=="None"):
				bbs.default_canvas_height=0
			else:
				bbs.default_canvas_height=int(self.request.get('default_canvas_height'))
		except:
			bbs.default_canvas_width=0
			bbs.default_canvas_height=0

		if(self.request.get('content_width')=="None"):
			bbs.content_width=800
		else:
			try:
				bbs.content_width=int(self.request.get('content_width'))
			except:
				bbs.content_width=800
		if(bbs.content_width<800):
			bbs.content_width=800
		if(bbs.content_width>1280):
			bbs.content_width=1280

		try:
			if(self.request.get('illust_reply_width')=="None"):
				bbs.illust_reply_width=400
			else:
				bbs.illust_reply_width=int(self.request.get('illust_reply_width'))
			if(self.request.get('illust_reply_height')=="None"):
				bbs.illust_reply_height=200
			else:
				bbs.illust_reply_height=int(self.request.get('illust_reply_height'))
		except:
			bbs.illust_reply_width=400
			bbs.illust_reply_height=200
		
		try:
			bbs.recent_comment_n=int(self.request.get('recent_comment_n'))
		except:
			bbs.recent_comment_n=8

		try:
			bbs.font_size=int(self.request.get('font_size'))
		except:
			bbs.font_size=0

		bbs.disable_counter=int(self.request.get('disable_counter'))
		bbs.disable_draw_time=int(self.request.get('disable_draw_time'))
		#bbs.disable_portal_menu=int(self.request.get('disable_portal_menu'))
		bbs.disable_news=int(self.request.get('disable_news'))
		bbs.disable_comment=int(self.request.get('disable_comment'))
		bbs.disable_tag=int(self.request.get('disable_tag'))
		bbs.default_order=int(self.request.get('order'))
		bbs.default_comment_order=int(self.request.get('comment_order'))
		bbs.comment_hidden_button=int(self.request.get('comment_hidden_button'))

		bbs.tweet_disable=int(self.request.get('tweet_disable'))
		bbs.twitter_enable=int(self.request.get('twitter_enable'))
		bbs.twitter_id=self.request.get('twitter_id')
		height=self.request.get('twitter_height')
		if(height=="None" or height==""):
			height="300"
		bbs.twitter_height=int(height)

		bbs.in_frame_mode=int(self.request.get('in_frame_mode'))
		
		bbs.button_color=self.request.get('button_color')
		bbs.button_active_color=self.request.get('button_active_color')
		if(bbs.button_color=="None"):
			bbs.button_color=""
		if(bbs.button_active_color=="None"):
			bbs.button_active_color=""

		amazon=self.request.get('amazon')
		amazon_title=self.request.get('amazon_title')
		freearea=self.request.get('freearea')
		freearea_title=self.request.get('freearea_title')
		comment_rule=self.request.get('comment_rule')
		if(amazon=="None"):
			amazon=""
		if(amazon_title=="None"):
			amazon_title=""
		if(freearea=="None"):
			freearea=""
		if(freearea_title=="None"):
			freearea_title=""
		if(comment_rule=="None"):
			comment_rule=""

		#summary = cgi.escape(summary)
		compiled_line = re.compile("\r\n|\r|\n")
		summary = compiled_line.sub(r'<br>', summary)
		freearea = compiled_line.sub(r'<br>', freearea)
		amazon = compiled_line.sub(r'<br>', amazon)
		comment_rule = compiled_line.sub(r'<br>', comment_rule)
		
		bbs.summary = summary
		bbs.amazon = amazon
		bbs.freearea = freearea
		bbs.comment_rule = comment_rule
		bbs.amazon_title = amazon_title
		bbs.freearea_title = freearea_title
		
		bbs.bg_color=bg_color
		bbs.font_color=font_color
		bbs.content_bg_color=content_bg_color
		bbs.content_font_color=content_font_color
		bbs.menu_bg_color=menu_bg_color
		bbs.menu_font_color=menu_font_color

		bbs.twitter_bg_color=twitter_bg_color
		bbs.twitter_font_color=twitter_font_color
		bbs.twitter_shell_color=twitter_shell_color
		bbs.side_color=side_color
		bbs.side_font_color=side_font_color
		bbs.disable_content_image=int(self.request.get("disable_content_image"))
		bbs.design_template_no=int(self.request.get("design_template_no"))
		bbs.bbs_mode=int(self.request.get("mode"))
		bbs.comment_rule_enable=int(self.request.get("comment_rule_enable"))
		bbs.category_list=self.request.get("category_list")
		bbs.enable_continue_draw=int(self.request.get("enable_continue_draw"))
		bbs.enable_illust_reply=int(self.request.get("enable_illust_reply"))
		bbs.enable_illust_reply_continue=int(self.request.get("enable_illust_reply_continue"))
		bbs.disable_normal_reply=int(self.request.get("disable_normal_reply"))
		bbs.enable_moper=int(self.request.get("enable_moper"))
		bbs.enable_full_flat=int(self.request.get("enable_full_flat"))
		bbs.disable_applause=int(self.request.get("disable_applause"))
		bbs.disable_analyze=int(self.request.get("disable_analyze"))
		#bbs.comment_login_require=int(self.request.get("comment_login_require"))
		bbs.disable_create_new_thread=int(self.request.get("disable_create_new_thread"))
		bbs.disable_create_new_illust=int(self.request.get("disable_create_new_illust"))
		bbs.dont_count_owner=int(self.request.get("dont_count_owner"))
		bbs.date_format=int(self.request.get("date_format"))
		bbs.move_account=self.request.get("move_account")
		bbs.show_only_movie=int(self.request.get("show_only_movie"))
		bbs.dont_permit_app=int(self.request.get("dont_permit_app"))
		bbs.delete_when_upload_success=int(self.request.get("delete_when_upload_success"))
		
		bbs.tool_bg_color=self.request.get("tool_bg_color")
		if(bbs.tool_bg_color=="None"):
			bbs.tool_bg_color=None
		
		if(self.request.get("page_illust_n")=="None"):
			bbs.page_illust_n=5
		else:
			bbs.page_illust_n=int(self.request.get("page_illust_n"))
		if(self.request.get("page_comment_n")=="None"):
			bbs.page_comment_n=10
		else:
			bbs.page_comment_n=int(self.request.get("page_comment_n"))
		if(bbs.page_illust_n<1) :bbs.page_illust_n=1
		if(bbs.page_illust_n>10) :bbs.page_illust_n=10
		if(bbs.page_comment_n<1) :bbs.page_comment_n=1
		if(bbs.page_comment_n>50) :bbs.page_comment_n=50
		
		#css
		css=self.request.get("css")
		if(not UpdateBbs.set_css(self,css,bbs)):
			return
		
		bbs.put()
		
		RecentCommentCache.invalidate(bbs);
		
		if(bbs.move_account):
			self.redirect(str('./move_account?bbs_key='+self.request.get("bbs_key")))
		else:
			self.redirect(str('./bbs_index?bbs_key='+self.request.get("bbs_key")))

	@staticmethod
	def set_css(main,css,bbs):
		if(css):
			if(css!=""):
				app=AppPortal.get_app(css)
				if(app==None):
					main.response.out.write(Alert.alert_msg("CSSデザインが見つかりません。",main.request.host))
					return False
				if(app.mode!=BbsConst.APP_MODE_CSS):
					main.response.out.write(Alert.alert_msg("CSSデザインではありません。",main.request.host))
					return False
				bbs.css=app
		return True
