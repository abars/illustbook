#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#MOPERプレイヤー

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from MesThread import MesThread
from Bbs import Bbs
from MappingId import MappingId
from Alert import Alert

class MoperPlayer(webapp.RequestHandler):
	def get(self):
		host_url="http://"+MappingId.mapping_host(self.request.host)+"/"
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
		
		template_values = {
		'host': host_url,
		'bbs': bbs,
		'bbs_key': bbs_key,
		'thread': thread,
		'thread_key': thread_key,
		'width': width,
		'height': height
		}		  
		path = os.path.join(os.path.dirname(__file__), '../html/moper_embedded.htm')
		self.response.out.write(template.render(path, template_values))
