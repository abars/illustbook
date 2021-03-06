#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#アカウントの移動

import cgi
import os
import sys
import re
import datetime
import random
import logging

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Counter import Counter
from myapp.Alert import Alert
from myapp.MappingId import MappingId

class MoveAccount(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		bbs=db.get(self.request.get("bbs_key"))

		url=self.request.path+"?bbs_key="+self.request.get("bbs_key")
		#login = users.create_login_url(url)
		#logout = users.create_logout_url(url)
		
		moveok=0
		if(user and bbs.move_account):
			if(bbs.move_account==user.email()):
				moveok=1
		
		exec_move=0
		if(self.request.get("mode")):
			if(self.request.get("mode")=="exec" and moveok==1):
				bbs.move_account=""
				bbs.owner=user
				bbs.user_id=user.user_id()
				bbs.put()
				exec_move=1
				
		template_values = {
			'host': "./",
            'user': user,
            'bbs': bbs,
#            'login': login,
#            'logout': logout,
            'moveok': moveok,
            'redirect_url': url,
            'exec_move': exec_move
		}

		path = '/html/move_account.html'
		self.response.out.write(template_select.render(path, template_values))
