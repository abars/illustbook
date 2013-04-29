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
from myapp.DelThread import DelThread
from myapp.ApiFeed import ApiFeed

class EditThreadList(webapp.RequestHandler):
	def post(self):
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			Alert.alert_msg_with_write(self,"掲示板の取得に失敗しました。")
			return

		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			Alert.alert_msg_with_write(self,"削除する権限がありません。")
			return

		thread_list=self.request.get_all("thread_list")

		count=0
		for thread in thread_list:
			try:
				thread=db.get(thread)
			except:
				continue
			try:
				thread_bbs=thread.bbs_key
			except:
				continue
			if(thread_bbs.key()==bbs.key()):
				DelThread.delete_thread_core(thread)
				count=count+1

		bbs.cached_thumbnail_key=None
		bbs.put()
		ApiFeed.invalidate_cache()

		page=self.request.get("page")
		url="./edit_thread_list?bbs_key="+str(bbs.key())+"&page="+str(page)+"&deleted_count="+str(count)
		self.redirect(str(url))

	def get(self):
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			Alert.alert_msg_with_write(self,"掲示板の取得に失敗しました。")
			return

		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			Alert.alert_msg_with_write(self,"削除する権限がありません。")
			return

		user = users.get_current_user()

		page=1
		if(self.request.get("page")):
			page=int(self.request.get("page"))
		
		limit=20
		offset=(page-1)*limit

		query=MesThread.all().filter("bbs_key =",bbs).order("-create_date")
		thread_list=query.fetch(offset=offset,limit=limit)

		deleted_count=self.request.get("deleted_count")

		template_values = {
			'host': './',
			'bbs': bbs,
			'user': user,
			'thread_list': thread_list,
			'redirect_url': self.request.path,
			'page': page,
			'deleted_count': deleted_count
		}

		path = os.path.join(os.path.dirname(__file__), '../html/edit_thread_list.html')
		self.response.out.write(template.render(path, template_values))
