#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドを削除する
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import os

import template_select

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
from myapp.CategoryList import CategoryList
from myapp.ApiObject import ApiObject
from myapp.SetUtf8 import SetUtf8

import logging

class EditThreadList(webapp.RequestHandler):
	def delete_thread(self,bbs):
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

		if(count):
			bbs.cached_thumbnail_key=None
			bbs.put()
			ApiFeed.invalidate_cache()
		return count

	def update_link(self,user):
		link_update=self.request.get("link_update")
		thread_list=link_update.split("/")
		count=0
		for thread in thread_list:
			try:
				thread=db.get(thread)
			except:
				continue
			if(thread.user_id):
				thread.user_id=None
			else:
				thread.user_id=user.user_id()
			thread.put()
			count=count+1
		return count

	def update_category(self):
		count=0
		category_update=self.request.get("category_update")
		category_list=category_update.split("/")
		for category_pair in category_list:
			thread_and_category=category_pair.split(":")
			try:
				thread=db.get(thread_and_category[0])
				thread.category=thread_and_category[1]
				thread.put()
				count=count+1
			except:
				continue
		return count

	def post(self):
		SetUtf8.set()

		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			Alert.alert_msg_with_write(self,"掲示板の取得に失敗しました。")
			return

		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			Alert.alert_msg_with_write(self,"削除する権限がありません。")
			return

		category_count=self.update_category()
		link_count=self.update_link(user)
		deleted_count=self.delete_thread(bbs)

		page=self.request.get("page")
		order=self.request.get("order")
		url="./edit_thread_list?bbs_key="+str(bbs.key())+"&page="+str(page)+"&order="+order+"&deleted_count="+str(deleted_count)+"&category_count="+str(category_count)+"&link_count="+str(link_count)
		self.redirect(str(url))

	def get(self):
		SetUtf8.set()

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

		order="new"
		if(self.request.get("order")):
			order=self.request.get("order")
		
		limit=20
		offset=(page-1)*limit

		query=db.Query(MesThread,keys_only=True)
		query.filter("bbs_key =",bbs)
		if(order=="new"):
			query.order("-create_date")
		else:
			query.order("create_date")

		thread_key_list=query.fetch(offset=offset,limit=limit)
		thread_list=[]
		for thread_key in thread_key_list:
			try:
				thread_list.append(db.get(thread_key))
			except:
				continue

		deleted_count=self.request.get("deleted_count")
		category_count=self.request.get("category_count")
		link_count=self.request.get("link_count")

		if(deleted_count):
			deleted_count=int(deleted_count)
		if(category_count):
			category_count=int(category_count)
		if(link_count):
			link_count=int(link_count)

		category_list=CategoryList.get_category_list(bbs)

		template_values = {
			'host': './',
			'bbs': bbs,
			'user': user,
			'thread_list': thread_list,
			'redirect_url': self.request.path,
			'page': page,
			'order': order,
			'deleted_count': deleted_count,
			'category_count': category_count,
			'link_count': link_count,
			'is_iphone': CssDesign.is_iphone(self),
			'is_tablet': CssDesign.is_tablet(self),
			'category_list': category_list,
			'is_english': CssDesign.is_english(self)
		}

		path = '/html/edit_thread_list.html'
		self.response.out.write(template_select.render(path, template_values))
