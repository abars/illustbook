#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#公開JavaScript API
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

import template_select

from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.MesThread import MesThread
from myapp.MappingId import MappingId
from myapp.Bbs import Bbs
from myapp.CssDesign import CssDesign
from myapp.ApiPerpetuation import ApiPerpetuation

class ApiJs(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()
		
		data=""

		user = users.get_current_user()
		user_id="";
		if(user):
			user_id=user.user_id()
		
		is_iphone=CssDesign.is_iphone(self)
		is_mobile=is_iphone or CssDesign.is_tablet(self)
		app_key=ApiPerpetuation.get_app_key(self)

		host_url=MappingId.mapping_host_with_scheme(self.request)+"/";

		template_values = {
			'host': host_url,
			'user_id': user_id,
			'is_mobile': is_mobile,
			'is_iphone': is_iphone,
			'app_key': app_key
		}

		self.response.content_type = 'text/javascript'
		path = "/html/api/illustbook.js"
		self.response.out.write(template_select.render(path, template_values))

