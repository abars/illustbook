#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#ローカルツール

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from MesThread import MesThread
from Bbs import Bbs
from MappingId import MappingId
from SetUtf8 import SetUtf8

class LocalTool(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		host_url ="./"
		template_values = {
			'host': host_url,
		}
		path = os.path.join(os.path.dirname(__file__), 'html/localtool.htm')
		render=template.render(path, template_values)
		self.response.out.write(render)		