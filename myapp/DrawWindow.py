#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#お絵描きツール画面
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

import template_select

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.Alert import Alert
from myapp.ReeditEscape import ReeditEscape
from myapp.CssDesign import CssDesign
from myapp.CategoryList import CategoryList
from myapp.EventList import EventList

class DrawWindow(webapp.RequestHandler):
	def get_thread_comment(self,template_values,thread_key,entry_key,is_reply):
		if(thread_key=="" or entry_key!="" or is_reply=="1"):
			return True
		try:
			thread=db.get(thread_key)
		except:
			thread=None
		if(thread==None):
			Alert.alert_msg_notfound(self)
			return False
		template_values["draw_time"]=thread.draw_time
		template_values["is_png"]=thread.is_png
		template_values["summary"]=ReeditEscape.escape(thread.summary)
		template_values["author"]=ReeditEscape.escape(thread.author)
		template_values["title"]=ReeditEscape.escape(thread.title)
		return True

	def get_entry_comment(self,template_values,entry_key):
		if(entry_key==""):
			return True
		try:
			entry=db.get(entry_key)
		except:
			entry=None
		if(entry==None):
			Alert.alert_msg_notfound(self)
			return False
		template_values["summary"]=ReeditEscape.escape(entry.content)
		template_values["author"]=ReeditEscape.escape(entry.editor)
		return True

	def get(self):
		celsys=0
		host_url=MappingId.mapping_host_with_scheme(self.request)+"/"

		bbs=None
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			bbs=None
		if(bbs==None):
			Alert.alert_msg_with_write(self,"イラストの投稿画面のURLが変更されています。掲示板からイラストを描くボタンをクリックして下さい。")
			return
		
		ipad=CssDesign.is_tablet(self)
		iphone=CssDesign.is_iphone(self)
		if(not ipad and not iphone):
			if(self.request.get("ipad") and self.request.get("ipad")=="1"):
				ipad=1
		
		thread_key=self.request.get("thread_key")
		entry_key=self.request.get("entry_key")

		category_list=CategoryList.get_category_list(bbs)
		event_list=EventList.get_event_list()

		user = users.get_current_user()
		logined=0
		if(user):
			logined=1

		is_reply=self.request.get("reply")

		wacom2=True
		#ipad=1

		#掲示板のデザインを取得
		design=CssDesign.get_design_object(self,bbs,host_url,1)

		#英語版かどうか
		is_english=CssDesign.is_english(self)
		
		#基本情報設定
		template_values = {
		'host': host_url,
		'bbs': bbs,
		'bbs_key': self.request.get("bbs_key"),
		'thread_key': thread_key,
		'entry_key': entry_key,
		'draw_time': 0,
		'canvas_width': int(self.request.get("canvas_width")),
		'canvas_height': int(self.request.get("canvas_height")),
		'canvas_url': self.request.get("canvas_url"),
		'reply': is_reply,
		'celsys': celsys,
		'category_list': category_list,
		'is_png': 0,
		'summary': "",
		'author': "",
		'title': "",
		'ipad': ipad,
		'logined': logined,
		'template_path':design["template_path"],
		'css_name':design["css_name"],
		'is_iphone':design["is_iphone"],
		'template_base_color':design["template_base_color"],
		'version': self.request.get("version"),
		'wacom2': wacom2,
		'selecting_category': None,
		'is_english': is_english,
		'event_list': event_list
		}

		#上書き時のコメントの初期値を設定
		if(not self.get_thread_comment(template_values,thread_key,entry_key,is_reply)):
			return
		if(not self.get_entry_comment(template_values,entry_key)):
			return
		
		if(ipad or iphone):
			path = '/html/tools/draw_window_ipad.htm'
		else:
			path = '/html/draw_window_flash_lapper.html'
		
		self.response.out.write(template_select.render(path, template_values))

