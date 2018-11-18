#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#まことじさんのコミックを表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

import template_select

from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MappingId import MappingId

class Comic(webapp.RequestHandler):
	def get(self):
		host_url=MappingId.mapping_host_with_scheme(self.request)+"/"
		page = 1
		if(self.request.get("page")):
			page=int(self.request.get("page"))
		
		template_values = {
		'host': host_url,
		'page': page
		}		  
		path = '/html/comic.html'
		self.response.out.write(template_select.render(path, template_values))

