#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#フォトアルバムの作成
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import logging

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

import template_select

from myapp.SetUtf8 import SetUtf8
from myapp.ApiObject import ApiObject
from myapp.ApiUser import ApiUser
from myapp.BbsConst import BbsConst
from myapp.MappingId import MappingId
from myapp.CssDesign import CssDesign

from myapp.UTC import UTC
from myapp.JST import JST

class Tolot(webapp.RequestHandler):
	def get(self,user_id,mode):
		SetUtf8.set()

		bookmark=ApiObject.get_bookmark_of_user_id(user_id)

		if(mode=="xml"):
			self.get_xml(user_id,bookmark)
		if(mode=="html"):
			self.get_guide(user_id,bookmark)

	def get_guide(self,user_id,bookmark):
		host=MappingId.mapping_host(self.request.host)
		host_url="http://"+host+"/";
		url=host_url+"tolot/"+str(user_id)+".xml"
		url=cgi.escape(url)
		user = users.get_current_user()

		template_values = {
			'user_id': user_id,
			'url': url,
			'host': host_url,
			'bookmark': bookmark,
			'is_iphone': CssDesign.is_iphone(self),
			'user': user,
			'redirect_url': self.request.path,
		}
		render=template_select.render("/html/tolot_guide.html", template_values)
		self.response.out.write(render)

	def get_xml(self,user_id,bookmark):
		offset=0
		limit=64
		illust_mode=BbsConst.ILLUSTMODE_ILLUST
		thread_list=ApiUser.user_get_thread_list_core(self,user_id,offset,limit,illust_mode)

		value=datetime.datetime.today()
		tmp=value.replace(tzinfo=UTC()).astimezone(JST())

		template_values = {
			'thread_list': thread_list,
			'bookmark': bookmark,
			'year': tmp.year,
			'month': tmp.month,
			'day': tmp.day,
			'hour': tmp.hour,
			'minute': tmp.minute
		}

		render=template_select.render("/html/tolot.xml", template_values)
		self.response.out.write(render)





















