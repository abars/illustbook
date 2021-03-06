#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#MOPER編集ツール
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

import template_select

from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.Alert import Alert
from myapp.ReeditEscape import ReeditEscape
from myapp.CssDesign import CssDesign

class MoperDraw(webapp.RequestHandler):
	def get(self):
		host_url=MappingId.mapping_host_with_scheme(self.request)+"/"
		bbs_key=self.request.get("bbs_key")
		thread_key=self.request.get("thread_key")
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			 bbs=None
		if(bbs==None):
			Alert.alert_msg_with_write(self,"ブックが見つかりません。")
			return

		ipad=CssDesign.is_tablet(self)
		iphone=CssDesign.is_iphone(self)
		if(ipad or iphone):
			Alert.alert_msg_with_write(self,"iPhoneやiPadでは動画お絵かきツールは使用できません。")
			return

		draw_time=0
		summary=""
		author=""
		title=""

		if(thread_key!=""):
			try:
				thread=db.get(thread_key)
			except:
				thread=None
			if(thread==None):
				Alert.alert_msg_with_write(self,"スレッドが見つかりません。")
				return
			draw_time=thread.draw_time

			summary=ReeditEscape.escape(thread.summary)
			author=ReeditEscape.escape(thread.author)
			title=ReeditEscape.escape(thread.title)

		canvas_url=self.request.get("canvas_url");
		if(canvas_url!=""):
			canvas_url=host_url+"moper_load?id="+canvas_url
			
		force=0
		canvas_width=400
		canvas_height=400
		if(self.request.get("canvas_width")):
			canvas_width=self.request.get("canvas_width")
		if(self.request.get("canvas_height")):
			canvas_height=self.request.get("canvas_height")
		if(self.request.get("force")):
			force=self.request.get("force")
		
		template_values = {
		'host': host_url,
		'bbs': bbs,
		'thread_key': thread_key,
		'bbs_key': bbs_key,
		'canvas_url': canvas_url,
		'canvas_width': canvas_width,
		'canvas_height': canvas_height,
		'force': force,
		'draw_time': draw_time,
		'summary': summary,
		'author': author,
		'title': title
		}
		path = '/html/tools/draw_window_moper.htm'
		self.response.out.write(template_select.render(path, template_values))

