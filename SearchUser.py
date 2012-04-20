#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザを検索（もういらないかも）
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import re
import os
import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from MesThread import MesThread
from BbsConst import BbsConst
from Bbs import Bbs
from Entry import Entry
from SetUtf8 import SetUtf8
from UTC import UTC
from JST import JST
from PageGenerate import PageGenerate

webapp.template.register_template_library('templatetags.django_filter')

class SearchUser(webapp.RequestHandler):		
	def get(self):
		name=self.request.get("name")
		thread_query=MesThread.all()
		thread_query.filter("author =",name)
		thread_query.filter("illust_mode !=",0)
		thread=thread_query.fetch(limit=100)

		host_url ="./"
		template_values = {
			'host': host_url,
			'threads':thread,
			'name':name
			}
		path = os.path.join(os.path.dirname(__file__), 'html/search.htm')
		render=template.render(path, template_values)
		self.response.out.write(render)		

