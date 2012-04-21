#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板のIDが空いているかを確認
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert

class CheckId(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()
		short=self.request.get('id')
		if(MappingId.key_format_check(short)):
			self.response.out.write(Alert.alert_msg("IDは半角英数である必要があります。",self.request.host))
			return
		if(MappingId.check_capability(short,"")==0):
			self.response.out.write(Alert.alert_msg("ID:"+short+"は既に登録されていて利用できません。",self.request.host))
			return
		self.response.out.write(Alert.alert_msg("ID:"+short+"は利用可能です。",self.request.host))
