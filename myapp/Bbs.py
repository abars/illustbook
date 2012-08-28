#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板構造体
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.Analyze import Analyze
from myapp.Counter import Counter
from myapp.BbsConst import BbsConst
from myapp.AppCode import AppCode

class Bbs(db.Model):
	bbs_name = db.StringProperty()
	summary = db.TextProperty()
	owner = db.UserProperty()	#deleted
	user_id = db.StringProperty()
	bg_color=db.StringProperty()
	side_color=db.StringProperty()
	side_font_color=db.StringProperty()
	side_background_image=db.StringProperty()
	font_color=db.StringProperty()
	counter = db.ReferenceProperty(Counter)
	bbs_mode =  db.IntegerProperty()
	my_homepage = db.StringProperty()
	official = db.IntegerProperty()
	illust_n = db.IntegerProperty()
	comment_n = db.IntegerProperty()
	applause_n = db.IntegerProperty()
	del_flag = db.IntegerProperty()
	background_image = db.StringProperty()
	bottom_image = db.StringProperty()
	button_color = db.StringProperty()
	button_active_color = db.StringProperty()
	enable_continue_draw = db.IntegerProperty()
	default_canvas_size = db.IntegerProperty()
	amazon = db.TextProperty()
	amazon_title=db.StringProperty()
	freearea = db.TextProperty()
	freearea_title = db.StringProperty()
	analyze = db.ReferenceProperty(Analyze)
	short = db.StringProperty()
	
	default_canvas_width = db.IntegerProperty()
	default_canvas_height = db.IntegerProperty()
	disable_counter = db.IntegerProperty()
	disable_draw_time = db.IntegerProperty()
	disable_portal_menu = db.IntegerProperty()
	disable_comment = db.IntegerProperty()
	in_frame_mode = db.IntegerProperty()
	spoit_mode = db.IntegerProperty()
	disable_news = db.IntegerProperty()

	enable_moper = db.IntegerProperty()
	enable_full_flat =db.IntegerProperty()				#一覧に本文
	enable_full_comment=db.IntegerProperty()		#一覧にコメント
	
	enable_illust_reply = db.IntegerProperty()
	enable_illust_reply_continue = db.IntegerProperty()
	disable_normal_reply = db.IntegerProperty()
	illust_reply_width = db.IntegerProperty()
	illust_reply_height = db.IntegerProperty()
	
	twitter_enable = db.IntegerProperty()
	twitter_id = db.StringProperty()
	twitter_font_color = db.StringProperty()
	twitter_bg_color = db.StringProperty()
	twitter_shell_color = db.StringProperty()
	twitter_height = db.IntegerProperty()
	
	tweet_disable = db.IntegerProperty()
	
	default_order = db.IntegerProperty()
	default_comment_order  = db.IntegerProperty()
	disable_applause = db.IntegerProperty()
	page_illust_n = db.IntegerProperty()
	page_comment_n = db.IntegerProperty()
	
	comment_login_require = db.IntegerProperty()
	disable_create_new_thread = db.IntegerProperty()
	disable_create_new_illust = db.IntegerProperty()

	content_bg_color=db.StringProperty()
	content_font_color=db.StringProperty()

	menu_bg_color=db.StringProperty()
	menu_font_color=db.StringProperty()
	
	comment_rule_enable=db.IntegerProperty()
	comment_rule=db.StringProperty()
	
	content_width=db.IntegerProperty()
	
	move_account=db.StringProperty()
	disable_analyze=db.IntegerProperty()
	
	category_list=db.TextProperty()
	design_template_no=db.IntegerProperty()
	
	disable_content_image=db.IntegerProperty()
	recent_comment_n=db.IntegerProperty()
	font_size=db.IntegerProperty()
	tool_bg_color=db.StringProperty()
	
	dont_count_owner=db.IntegerProperty()							#オーナーのアクセスをカウントするか
	disable_tag=db.IntegerProperty()										#タグフォームを非表示にするか
	date_format = db.IntegerProperty()									#日付の表記 0:年月日時秒 1:年月日
	show_only_movie = db.IntegerProperty()							#イラスト一覧に動画のみ表示
	bookmark_count = db.IntegerProperty()							#ブックマーク数
	dont_permit_app = db.IntegerProperty()							#イラストのアプリでの使用禁止
	css = db.ReferenceProperty(AppCode)								#CSSデザイン
	delete_when_upload_success=db.IntegerProperty()			#アップロードに成功した場合にデータを削除するか
	comment_hidden_button = db.IntegerProperty()				#コメント非表示ボタンを表示するか
	
	cached_thumbnail_key = db.StringProperty()					#サムネイルへのKey

	create_date = 	db.DateTimeProperty(auto_now=False)
	date = db.DateTimeProperty(auto_now=True)

	def put(self,**kwargs):
		super(Bbs, self).put(**kwargs)
		if(self.key()):
			memcache.delete(BbsConst.OBJECT_CACHE_HEADER+str(self.key()))
	
	def get_category_list(self):
		category_list=[]
		if(self.category_list and self.category_list!=""):
			category_list=self.category_list.split(",")
		else:
			self.category_list=""
		return category_list

	def add_new_category(self,category):
		category_list=self.get_category_list()
		if not (category in category_list):
			self.category_list=self.category_list+","+category
			self.put()
