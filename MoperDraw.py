#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#MOPERツール

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from MesThread import MesThread
from Bbs import Bbs
from MappingId import MappingId
from Alert import Alert
from ReeditEscape import ReeditEscape

class MoperDraw(webapp.RequestHandler):
	def get(self):
		host_url="http://"+MappingId.mapping_host(self.request.host)+"/"
		bbs_key=self.request.get("bbs_key")
		thread_key=self.request.get("thread_key")
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			 bbs=None
		if(bbs==None):
			self.response.out.write(Alert.alert_msg("ブックが見つかりません。",self.request.host))
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
				self.response.out.write(Alert.alert_msg("スレッドが見つかりません。",self.request.host))
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
		path = os.path.join(os.path.dirname(__file__), 'moper.htm')
		self.response.out.write(template.render(path, template_values))

