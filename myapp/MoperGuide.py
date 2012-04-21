#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#MOPERの使い方
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId

class MoperGuide(webapp.RequestHandler):
	def get(self):
		template_values = {
			'temp': 0,
		}
		path = os.path.join(os.path.dirname(__file__), '../html/moper_guide.html')
		self.response.out.write(template.render(path, template_values))