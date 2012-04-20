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

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from Bbs import Bbs
from Counter import Counter
from Alert import Alert
from MappingId import MappingId

class MoveAccount(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		bbs=db.get(self.request.get("bbs_key"))

		url="http://www.illustbook.net/move_account?bbs_key="+self.request.get("bbs_key")
		login = users.create_login_url(url)
		logout = users.create_logout_url(url)
		
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
            'login': login,
            'logout': logout,
            'moveok': moveok,
            'exec_move': exec_move
		}

		path = os.path.join(os.path.dirname(__file__), 'mes_move_account.html')
		self.response.out.write(template.render(path, template_values))
