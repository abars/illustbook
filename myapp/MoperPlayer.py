#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#MOPERプレイヤー

import os

import template_select
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.Alert import Alert
from myapp.CssDesign import CssDesign

class MoperPlayer(webapp.RequestHandler):
	def get(self):
		host_url=MappingId.mapping_host_with_scheme(self.request)+"/"
		bbs_key=self.request.get("bbs_key")
		thread_key=self.request.get("thread_key")

		try:
			bbs = db.get(self.request.get("bbs_key"))
			thread = db.get(self.request.get("thread_key"))
		except:
			bbs = None
			thread = None
		
		if(bbs==None or thread==None):
			self.response.out.write(Alert.alert_msg("スレッドが見つかりません。",self.request.host))
			return
		
		image=thread.image_key#db.get(thread.image);
		width=400
		height=400
		if(image.width):
			width=image.width
		if(image.height):
			height=image.height
		if(self.request.get("width")):
			width=self.request.get("width")
		if(self.request.get("height")):
			height=self.request.get("height")
		
		if(CssDesign.is_iphone(self)==1):
			if(width>=300):
				height=300*height/width
				width=300
		
		template_values = {
		'host': host_url,
		'bbs': bbs,
		'bbs_key': bbs_key,
		'thread': thread,
		'thread_key': thread_key,
		'width': width,
		'height': height
		}		  
		path = '/html/moper/moper_embedded.htm'
		self.response.out.write(template_select.render(path, template_values))
