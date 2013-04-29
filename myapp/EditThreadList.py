#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドを削除する
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.Alert import Alert
from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
from myapp.OwnerCheck import OwnerCheck
from myapp.BbsConst import BbsConst
from myapp.AppCode import AppCode
from myapp.CssDesign import CssDesign

class EditThreadList(webapp.RequestHandler):
	def post(self):
		return

	def get(self):
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			Alert.alert_msg_with_write(self,"掲示板の取得に失敗しました。")
			return

		user = users.get_current_user()

		page=1
		if(self.request.get("page")):
			page=int(self.request.get("page"))
		
		limit=20
		offset=(page-1)*limit

		thread_list=MesThread.all().order("-create_date").fetch(offset=offset,limit=limit)

		template_values = {
			'host': './',
			'bbs': bbs,
			'user': user,
			'thread_list': thread_list,
			'redirect_url': self.request.path,
			'page': page
		}

		path = os.path.join(os.path.dirname(__file__), '../html/edit_thread_list.html')
		self.response.out.write(template.render(path, template_values))
