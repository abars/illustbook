#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#リダイレクト
#copyright 2010-2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

from google.appengine.ext import webapp

import template_select
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Alert import Alert
from myapp.MappingId import MappingId
from myapp.MesThread import MesThread

import template_select

class RedirectBbs(webapp.RequestHandler):
	def get(self):
		try:
			bbs=db.get(self.request.get("bbs_key"))
		except:
			bbs=None
		if(bbs==None):
			self.response.out.write(Alert.alert_msg_notfound(self.request.host))
			return			
		host_name=self.request.host
		if(host_name=="http://www.illust-book.appspot.com/"):
			host_name="http://www.illustbook.net/";		
		host_url="http://"+MappingId.mapping_host(host_name)+"/";
		url=MappingId.get_usr_url(host_url,bbs)
		self.redirect(str(url))
