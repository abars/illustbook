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

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

from django.utils import simplejson

webapp.template.register_template_library('templatetags.django_filter')

from SetUtf8 import SetUtf8
from Alert import Alert
from MesThread import MesThread
from MappingId import MappingId
from Bbs import Bbs
from CssDesign import CssDesign
from ApiPerpetuation import ApiPerpetuation

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

		host_url="http://"+MappingId.mapping_host(self.request.host)+"/";

		template_values = {
			'host': host_url,
			'user_id': user_id,
			'is_mobile': is_mobile,
			'is_iphone': is_iphone,
			'app_key': app_key
		}

		self.response.content_type = 'text/javascript'
		path = os.path.join(os.path.dirname(__file__), "../api/illustbook.js")
		self.response.out.write(template.render(path, template_values))

