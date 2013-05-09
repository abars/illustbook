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

class DrawWindow(webapp.RequestHandler):
	def get(self):
		celsys=0
		host_url="http://"+MappingId.mapping_host(self.request.host)+"/"

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
		draw_time=0
		is_png=0
		summary=""
		author=""
		title=""
		if(thread_key!=""):
			try:
				thread=db.get(thread_key)
			except:
				thread=None
			if(thread==None):
				self.response.out.write(Alert.alert_msg_notfound(self.request.host))
				return
			draw_time=thread.draw_time
			is_png=thread.is_png

			summary=ReeditEscape.escape(thread.summary)
			author=ReeditEscape.escape(thread.author)
			title=ReeditEscape.escape(thread.title)

		category_list=CategoryList.get_category_list(bbs)

		user = users.get_current_user()
		logined=0
		if(user):
			logined=1

		is_reply=self.request.get("reply")
		if(is_reply):
			summary=""
			author=""

		wacom2=self.request.get("wacom2")
		wacom2=True

		#掲示板のデザインを取得
		design=CssDesign.get_design_object(self,bbs,host_url,1)
		
		template_values = {
		'host': host_url,
		'bbs': bbs,
		'bbs_key': self.request.get("bbs_key"),
		'thread_key': thread_key,
		'draw_time': draw_time,
		'canvas_width': int(self.request.get("canvas_width")),
		'canvas_height': int(self.request.get("canvas_height")),
		'canvas_url': self.request.get("canvas_url"),
		'reply': is_reply,
		'celsys': celsys,
		'category_list': category_list,
		'is_png': is_png,
		'summary': summary,
		'author': author,
		'title': title,
		'ipad': ipad,
		'logined': logined,
		'template_path':design["template_path"],
		'css_name':design["css_name"],
		'is_iphone':design["is_iphone"],
		'template_base_color':design["template_base_color"],
		'version': self.request.get("version"),
		'wacom2': wacom2,
		'selecting_category': None
		}
		
		if(ipad or iphone):
			path = '/html/tools/draw_window_ipad.htm'
		else:
			path = '/html/draw_window_flash_lapper.html'
		
		self.response.out.write(template_select.render(path, template_values))

