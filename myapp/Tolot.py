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

from myapp.UTC import UTC
from myapp.JST import JST

class Tolot(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()
		mode=self.request.get("mode")
		user_id=self.request.get("user_id")

		if(mode=="xml"):
			self.get_xml(user_id)
		else:
			self.get_guide(user_id)

	def get_guide(self,user_id):
		host_url="http://"+MappingId.mapping_host(self.request.host)+"/";
		template_values = {
			'user_id': user_id,
			'host_url': host_url
		}
		render=template_select.render("/html/tolot_guide.html", template_values)
		self.response.out.write(render)

	def get_xml(self,user_id):
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)

		offset=0
		limit=1
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





















