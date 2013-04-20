#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#DropBox redirect
#copyright 2010-2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

from google.appengine.ext import webapp

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

webapp.template.register_template_library('templatetags.django_filter')

class DropBox(webapp.RequestHandler):
	def get(self):
		template_values = {
			'host': "./"
		}
		path = os.path.join(os.path.dirname(__file__), '../html/dropbox.html')
		self.response.out.write(template.render(path, template_values))