#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#規約違反
#

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from MesThread import MesThread
from BbsConst import BbsConst
from Bbs import Bbs
from SetUtf8 import SetUtf8
from PageGenerate import PageGenerate
from MappingId import MappingId
from ApiFeed import ApiFeed
from OwnerCheck import OwnerCheck

class ViolationTerms(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		user = users.get_current_user()
		if(user):
			if(OwnerCheck.is_admin(user)):
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

