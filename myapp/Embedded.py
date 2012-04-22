#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#埋め込みタグを取得
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert

class Embedded(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		try:
			thread = db.get(self.request.get("thread_key"))
			bbs=thread.bbs_key
		except:
			thread=None
			bbs=None

		if(bbs == None):
			self.response.out.write(Alert.alert_msg_notfound(self.request.host))
			return
		
		host_url="http://"+MappingId.mapping_host(self.request.host)+"/"
		
		link=host_url
		
		if(bbs.short):
			link=link+""+bbs.short+"/"
		else:
			link=link+"usr/"+str(bbs.key())+"/"
		link+=str(thread.key())+".html"
		
		moper=""
		if(thread.illust_mode==2):
			moper='<script type="text/javascript" src="'+host_url+'moper_player?bbs_key='+str(bbs.key())+'&thread_key='+str(thread.key())+'"></script>';
		
		img=host_url+"img/"+str(thread.image)+".jpg"
				
		template_values = {
			'host': host_url,
			'bbs': bbs,
			'thread': thread,
			'link':link,
			'img':img,
			'moper':moper
			}
		path = os.path.join(os.path.dirname(__file__), '../html/embedded.html')
		self.response.out.write(template.render(path, template_values))
		
