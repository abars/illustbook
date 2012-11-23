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
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.ChatRoom import ChatRoom
from myapp.Chat import Chat

class ChatConnected(webapp.RequestHandler):
	def post(self):
		client_id = self.request.get('from')

		#PCではDisconnectは本当の切断時にしか来ないが、
		#iOSでは時々、Disconnect->Connectで再接続が来る
		#そのため、クライアントIDを一度でも使ったことのあるルームを覚えておき、
		#そこに再接続する必要がある

		#クライアントが属しているルームに接続通知を送る
		query=ChatRoom.all()
		query.filter("channel_client_list =",client_id)
		room_list=query.fetch(offset=0,limit=100)
		for room in room_list:
			Chat.user_update_notify(room)

		#再接続に対応するために属していたルームに再接続する
		query=ChatRoom.all()
		query.filter("channel_client_list_for_reconnect =",client_id)
		room_list=query.fetch(offset=0,limit=100)
		for room in room_list:
			if(not(client_id in room.channel_client_list)):
				Chat.add_user(room.key(),client_id)

		logging.info("### connect user "+client_id)



