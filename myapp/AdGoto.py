#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#Ad redirect
#copyright 2010-2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

import template_select

from google.appengine.ext import webapp

from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

class AdGoto(webapp.RequestHandler):
	def get(self):
		template_values = {
			'host': "./"
		}
		path = '/html/adsense/ad_goto.html'
		self.response.out.write(template_select.render(path, template_values))