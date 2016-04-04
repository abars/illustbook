#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#イベントを追加する
#copyright 2014 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging
import base64
import re

from collections import OrderedDict

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Event import Event
from myapp.Alert import Alert
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.MappingId import MappingId
from myapp.EscapeComment import EscapeComment

class EventList(webapp.RequestHandler):
	@staticmethod
	def get_event_list():
		now_date=datetime.datetime.today()
		event_query=Event.all()
		event_query.filter("start_date <=",now_date)
		event_list=event_query.fetch(offset=0,limit=100)
		event_list_filter=[]
		for event in event_list:
			if(event.end_date>now_date):
				event_list_filter.append(event)
		return event_list_filter

	@staticmethod
	def get_all_event_list():
		now_date=datetime.datetime.today()
		event_query=Event.all()
		event_query.filter("start_date >",now_date)
		return event_query.fetch(offset=0,limit=100)

	@staticmethod
	def get_old_event_list():
		now_date=datetime.datetime.today()
		event_query=Event.all()
		event_query.filter("end_date <",now_date).order("-end_date")
		return event_query.fetch(offset=0,limit=100)

	@staticmethod
	def is_old_event(event):
		if(not event):
			return False
		now_date=datetime.datetime.today()
		if(event.end_date<now_date):
			return True
		return False

	@staticmethod
	def get_event(event_id):
		event_list=Event.all().filter("id =",event_id).fetch(offset=0,limit=1)
		if(event_list):
			return event_list[0]
		return None

	def _update(self,event,user,validate_all,auto_link):
		event.title=self.request.get("title")
		event.summary=self.request.get("summary")

		if(auto_link):
			event.summary=EscapeComment.escape_br(event.summary)
			event.summary=EscapeComment.auto_link(event.summary)

		event.id=self.request.get("id")
		if(event.id==""):
			Alert.alert_msg_with_write(self,"IDを入力する必要があります。")
			return False
		if(MappingId.key_format_check(event.id)):
			Alert.alert_msg_with_write(self,"IDは半角英数で16文字以下である必要があります。")
			return False

		try:
			event.start_date=datetime.datetime.strptime(self.request.get("start_date"), '%Y/%m/%d').replace(tzinfo=JST()).astimezone(UTC())
			event.end_date=datetime.datetime.strptime(self.request.get("end_date"), '%Y/%m/%d').replace(tzinfo=JST()).astimezone(UTC())
		except:
			Alert.alert_msg_with_write(self,"日付の変換に失敗しました。")
			return False

		if(event.end_date <= event.start_date):
			Alert.alert_msg_with_write(self,"終了日の方が開始日より早くなっています。")
			return False

		event_list=Event.all().filter("start_date <=",event.end_date).order("-start_date").fetch(limit=1)	#既存のDBが重複していないと仮定すると最新の1つだけチェックすればよい
		for e in event_list:
			if(e.id==event.id):
				continue
			err=False
			if(e.start_date.replace(tzinfo=UTC()).astimezone(UTC()) <= event.start_date):
				if(e.end_date.replace(tzinfo=UTC()).astimezone(UTC()) > event.start_date):
					err=True
			if(e.start_date.replace(tzinfo=UTC()).astimezone(UTC()) < event.end_date):
				if(e.end_date.replace(tzinfo=UTC()).astimezone(UTC()) > event.end_date):
					err=True
			if(err):
				mes ="今回のイベント&nbsp;"+str(event.start_date.replace(tzinfo=UTC()).astimezone(JST()).strftime('%Y/%m/%d'))+"〜"+str(event.end_date.replace(tzinfo=UTC()).astimezone(JST()).strftime('%Y/%m/%d'))+"<br/>";
				mes+="他のイベント&nbsp;"+str(e.start_date.replace(tzinfo=UTC()).astimezone(JST()).strftime('%Y/%m/%d'))+"〜"+str(e.end_date.replace(tzinfo=UTC()).astimezone(JST()).strftime('%Y/%m/%d'))+"<br/>";
				Alert.alert_msg_with_write(self,"日程が他のイベントと重複しています。<br/>"+mes)
				return False

		if(event.end_date - event.start_date > datetime.timedelta(days=7)):
			Alert.alert_msg_with_write(self,"日程が一週間を超えています。")
			return False

		if(validate_all):
			if(event.title=="" or event.id==""):
				Alert.alert_msg_with_write(self,"タイトルとIDを入力して下さい。")
				return False
		event.user_id=user.user_id()
		event.author=self.request.get("author")
		return True

	def get(self,mode_url):
		mode=self.request.get("mode")

		if(mode=="edit"):
			event=Event.all().filter("id =",self.request.get("id")).fetch(limit=2)
			if(not event or len(event)==0):
				Alert.alert_msg_with_write(self,"イベントが存在しません")
				return
		else:
			if(Event.all().filter("id =",self.request.get("id")).count()>=1):
				Alert.alert_msg_with_write(self,"このIDは既に使われています")
				return

		user = users.get_current_user()
		event=Event()
		if(not self._update(event,user,False,False)):
			return
		Alert.alert_msg_with_write(self,"このイベントは作成可能です")

	def post(self,mode_url):
		mode=self.request.get("mode")

		user = users.get_current_user()
		if(not user):
			Alert.alert_msg_with_write(self,"ログインが必要です。")
			return

		msg=""

		if(mode=="add"):
			if(Event.all().filter("id =",self.request.get("id")).count()>=1):
				Alert.alert_msg_with_write(self,"このIDのイベントは既に存在しています")
				return
			
			event=Event()
			if(not self._update(event,user,True,True)):
				return
			event.put()

		if(mode=="edit"):
			event=Event.all().filter("id =",self.request.get("id")).fetch(limit=2)
			if(not event or len(event)==0):
				Alert.alert_msg_with_write(self,"イベントが存在しません")
				return
			if(len(event)>=2):
				Alert.alert_msg_with_write(self,"イベントが重複しています")
				return
			event=event[0]
			if(not self._update(event,user,True,False)):
				return
			event.put()

		if(mode=="del"):
			event=Event.all().filter("id =",self.request.get("id")).fetch(limit=2)
			if(not event or len(event)==0):
				Alert.alert_msg_with_write(self,"イベントが存在しません")
				return
			event[0].delete()

		host="http://"+self.request.host+"/"

		if(mode=="del"):
			self.redirect(str(host+"?order=event"))
		else:
			self.redirect(str(host+"?order=event&event_id="+event.id))




