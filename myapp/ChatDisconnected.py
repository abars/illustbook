#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#イラブチャット
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import time
import datetime
import random
import logging
import base64

from google.appengine.api import channel
import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.ChatRoom import ChatRoom
from myapp.Chat import Chat

class ChatDisconnected(webapp.RequestHandler):
	def post(self):
		client_id = self.request.get('from')
		query=ChatRoom.all()
		query.filter("channel_client_list =",client_id)
		room_list=query.fetch(offset=0,limit=100)
		for room in room_list:
			Chat.remove_user(room.key(),client_id)
		logging.info("### disconnect user "+client_id)



