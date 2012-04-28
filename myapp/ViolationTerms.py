#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#規約違反を報告する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.Bbs import Bbs
from myapp.SetUtf8 import SetUtf8
from myapp.PageGenerate import PageGenerate
from myapp.MappingId import MappingId
from myapp.ApiFeed import ApiFeed
from myapp.OwnerCheck import OwnerCheck
from myapp.Alert import Alert

class ViolationTerms(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		user = users.get_current_user()
		if(user):
			if(not OwnerCheck.is_admin(user)):
				self.response.out.write(Alert.alert_msg("権限がありません。",self.request.host))
				return

		thread = db.get(self.request.get("thread_key"))
		bbs = db.get(self.request.get("bbs_key"))
		
		if(self.request.get("mode")=="adult"):
			if(thread.adult):
				thread.adult=0
			else:
				thread.adult=1

		if(self.request.get("mode")=="terms"):
			if(thread.violate_terms):
				thread.violate_terms=0
			else:
				thread.violate_terms=1
		
		if(self.request.get("mode")=="photo"):
			if(thread.violate_photo):
				thread.violate_photo=0
			else:
				thread.violate_photo=1
		thread.put()
		
		ApiFeed.invalidate_cache()
		
		self.redirect(str(MappingId.get_usr_url("./",bbs)+self.request.get("thread_key")+".html"))

