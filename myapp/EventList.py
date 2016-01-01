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

	def get(self,mode):
		if(mode=="add"):
			event=Event()
			event.title=self.request.get("title")
			event.summary=self.request.get("summary")
			event.id=self.request.get("id")
			event.start_date=datetime.datetime.strptime(self.request.get("start_date"), '%Y-%m-%d').replace(tzinfo=JST()).astimezone(UTC())
			event.end_date=datetime.datetime.strptime(self.request.get("end_date"), '%Y-%m-%d').replace(tzinfo=JST()).astimezone(UTC())
			if(event.title=="" or event.id==""):
				Alert.alert_msg_with_write(self,"タイトルとIDを入力して下さい。")
				return
			event.put()
			Alert.alert_msg_with_write(self,"イベントを登録しました。")


