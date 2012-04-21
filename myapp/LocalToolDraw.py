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

from MesThread import MesThread
from Bbs import Bbs
from MappingId import MappingId
from SetUtf8 import SetUtf8

class LocalToolDraw(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		celsys=0
		if(self.request.get("celsys")=="1"):
				celsys=1

		host_url ="./"
		template_values = {
			'host': host_url,
			'canvas_width': self.request.get("canvas_width"),
	  		'canvas_height': self.request.get("canvas_height"),
	  		'celsys': celsys
		}
		path = os.path.join(os.path.dirname(__file__), '../html/localtool_draw.htm')
		render=template.render(path, template_values)
		self.response.out.write(render)		