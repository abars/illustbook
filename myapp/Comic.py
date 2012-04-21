#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#まことじさんのコミックを表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from MappingId import MappingId

class Comic(webapp.RequestHandler):
	def get(self):
		host_url="http://"+MappingId.mapping_host(self.request.host)+"/"
		page = 1
		if(self.request.get("page")):
			page=int(self.request.get("page"))
		
		template_values = {
		'host': host_url,
		'page': page
		}		  
		path = os.path.join(os.path.dirname(__file__), '../html/comic.htm')
		self.response.out.write(template.render(path, template_values))

