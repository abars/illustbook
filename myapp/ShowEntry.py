#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#コメントを表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Counter import Counter
from myapp.Alert import Alert
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Entry import Entry
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.CssDesign import CssDesign
from myapp.BbsConst import BbsConst
from myapp.MappingThreadId import MappingThreadId
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.CounterWorker import CounterWorker
from myapp.ApiObject import ApiObject

class ShowEntry(webapp.RequestHandler):
	@staticmethod
	def _get_response(com_list_,thread):
		#コメントソート
		if(thread.illust_mode):
			com_list_.reverse()
		
		#レスを取得
		com_list=[]
		for com in com_list_:
			res_list=[]
			for res in com.res_list:
				res_list.append(db.get(res))
			com_list.append({'com':com, 'res_list':res_list})
		return com_list
	
	#コメントのレンダリング
	@staticmethod
	def render_comment(req,host_url,bbs,thread,com_list_,edit_flag,bbs_key,logined,show_comment_form):
		#レスを取得
		com_list=ShowEntry._get_response(com_list_,thread)
		
		#レンダリング
		template_values = {
			'host': host_url,
			'bbs': bbs,
			'thread': thread,
			'com_list':com_list,
			'edit_flag':edit_flag,
			'bbs_key': bbs_key,
			'logined':logined,
			'show_comment_form':show_comment_form
			}

		path = os.path.join(os.path.dirname(__file__), "../html/thread/thread_comment.html")
		return template.render(path, template_values)
		

