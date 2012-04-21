#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ブックマークしているユーザを表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
from myapp.MappingThreadId import MappingThreadId
from myapp.Alert import Alert
from myapp.SetUtf8 import SetUtf8
from myapp.RecentTag import RecentTag
from myapp.Bookmark import Bookmark
from myapp.CssDesign import CssDesign

class ShowBookmark(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		#オブジェクト取得
		thread=None
		if(self.request.get("thread_key")):
			try:
				thread = db.get(self.request.get("thread_key"))
			except:
				thread=None

		bbs=None
		if(self.request.get("bbs_key")):
			try:
				bbs = db.get(self.request.get("bbs_key"))
			except:
				bbs=None

		app=None
		if(self.request.get("app_key")):
			try:
				app = db.get(self.request.get("app_key"))
			except:
				app=None
		
		#iPhoneかどうか
		is_iphone=CssDesign.is_iphone(self)
		
		template_values = {
			'host': "./",
			'search_thread': thread,
			'search_bbs': bbs,
			'search_app': app,
			'is_iphone': is_iphone,
			'user': users.get_current_user(),
			'redirect_url': self.request.path
		}
		
		path = os.path.join(os.path.dirname(__file__), '../html/portal/general_show_bookmark.html')
		self.response.out.write(template.render(path, template_values))
		

