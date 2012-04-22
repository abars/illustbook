#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#イラブペイントだけを使うお客様向け
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8

class LocalTool(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		host_url ="./"
		template_values = {
			'host': host_url,
		}
		path = os.path.join(os.path.dirname(__file__), '../html/tools/localtool.htm')
		render=template.render(path, template_values)
		self.response.out.write(render)		