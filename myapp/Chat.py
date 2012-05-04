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

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Alert import Alert
from myapp.SetUtf8 import SetUtf8
from myapp.Bookmark import Bookmark
from myapp.CssDesign import CssDesign
from myapp.ChatRoom import ChatRoom
from myapp.ApiObject import ApiObject

class Chat(webapp.RequestHandler):
	#ユーザ名を取得する
	def get_user_name(self,user):
		bookmark=ApiObject.get_bookmark_of_user_id(user.user_id())
		user_name="名無しさん"
		if(bookmark and bookmark.name and bookmark.name!="None"):
			user_name=bookmark.name
		return user_name

	#ルームを作成する
	def create_room(self,user):
		if(self.request.get("name")==""):
			self.response.out.write(Alert.alert_msg("ルーム名は必須です。",self.request.host))
			return
		if(not user):
			self.response.out.write(Alert.alert_msg("ルームの作成にはログインが必要です。",self.request.host))
			return

		user_name=self.get_user_name(user)

		room=ChatRoom()
		room.name=self.request.get("name")
		room.user_id=user.user_id()
		room.user_name=user_name
		room.command_list=""
		room.command_cnt=0
		room.user_count=0
		room.create_date=datetime.datetime.now()
		room.put()
		self.redirect("./chat")
	
	#ルームを終了する
	def close_room(self,user):
		try:
			room=db.get(self.request.get("key"))
		except:
			room=None
		if(not room):
			self.response.out.write(Alert.alert_msg("ルームが見つかりません。",self.request.host))
			return
		if(not user or room.user_id!=user.user_id()):
			self.response.out.write(Alert.alert_msg("終了する権限がありません。",self.request.host))
			return
		room.delete()
		self.redirect("./chat")
	
	#ルームにコマンドを送る
	def post_command(self):
		key=self.request.get("key")
		cmd_count=int(self.request.get("command_count"))
		user_count=int(self.request.get("user_count"))
		
		cmd_list=""
		for i in range(0,cmd_count):
			cmd=self.request.get("command"+str(i))
			if(not cmd):
				cmd_list=None
				break
			cmd_list=cmd_list+cmd
			if(i!=cmd_count-1):
				cmd_list=cmd_list+" , "
		
		if(not cmd_list):
			ApiObject.write_json_core(self,{"status":"failed"})
			return

		try:
			size=db.run_in_transaction(Chat.post_command_core,key,cmd_list,cmd_count,user_count)	#排他制御を行う
			ApiObject.write_json_core(self,{"status":"success","size":size})
		except:
			ApiObject.write_json_core(self,{"status":"failed"})
	
	@staticmethod
	def post_command_core(key,cmd,cmd_count,user_count):
		room=db.get(key)
		room.user_count=user_count
		if(room.command_list==""):
			room.command_list=cmd
		else:
			room.command_list=room.command_list+" , "+cmd
		room.command_cnt=room.command_cnt+cmd_count
		room.put()
		return sys.getsizeof(room.command_list)+sys.getsizeof(room)
		
	#コマンドを取得する
	def get_command(self):
		room=db.get(self.request.get("key"))

		offset=int(self.request.get("offset"))
		limit=int(self.request.get("limit"))
		
		now_len=room.command_cnt
		if (offset+limit)>now_len:
			limit=now_len-offset
		
		server_command_list=room.command_list.split(" , ")
		
		command_list=[]
		for i in range(offset,offset+limit):
			one_cmd=server_command_list[i]
			command_list.append(one_cmd)
		
		ApiObject.write_json_core(self,{"status":"success","offset":offset,"count":limit,"command_list":command_list})
	
	#ポータル
	def show_portal(self,user):
		is_iphone=CssDesign.is_iphone(self)
		room_list=ChatRoom.all().fetch(limit=10)
		
		show_room=[]
		for room in room_list:
			room.from_last_update=(Chat.get_sec(datetime.datetime.now())-Chat.get_sec(room.date))/60
			room.from_created=(Chat.get_sec(datetime.datetime.now())-Chat.get_sec(room.create_date))/60
			if(room.from_last_update>=10):
				room.delete()
			else:
				if(room.from_last_update>=1 and room.user_count>=1):
					room.user_count=0
				show_room.append(room)
		
		template_values = {
			'host': "./",
			'is_iphone': is_iphone,
			'user': user,
			'redirect_url': self.request.path,
			'mode': "chat",
			'header_enable': False,
			'room_list': show_room
		}
		path = os.path.join(os.path.dirname(__file__), '../html/portal.html')
		self.response.out.write(template.render(path, template_values))
	
	#経過時間取得
	@staticmethod
	def get_sec(now):
		return int(time.mktime(now.timetuple()))
	
	#チャットツール
	def tool(self,user):
		bbs=None
		bbs_key=""
		thread_key=""
		canvas_width=600
		canvas_height=600
		room_key=self.request.get("key")
		ipad=CssDesign.is_tablet(self)
		
		if(not user):
			self.response.out.write(Alert.alert_msg("ルームへの参加にはログインが必要です。",self.request.host))
			return

		user_id=user.user_id()
		user_name=self.get_user_name(user)
		server_time=Chat.get_sec(datetime.datetime.now())

		template_values = {
		'host': "./",
		'bbs': bbs,
		'bbs_key': bbs_key,
		'thread_key': thread_key,
		'draw_time': "",
		'canvas_width': canvas_width,
		'canvas_height': canvas_height,
		'canvas_url': "",
		'reply': False,
		'summary': "",
		'author': "",
		'title': "",
		'chat': room_key,
		'ipad': ipad,
		'user_id':user_id,
		'user_name':user_name,
		'server_time':server_time
		}
		
		path = os.path.join(os.path.dirname(__file__), '../html/tools/draw_window_ipad.htm')
		self.response.out.write(template.render(path, template_values))
	
	#インタフェース
	def post(self):
		mode=self.request.get("mode")
		if(mode=="post_command"):
			self.post_command()
			return
		
	def get(self):
		SetUtf8.set()

		#ユーザ取得
		user=users.get_current_user()

		#モード取得
		mode=self.request.get("mode")
		if(mode=="create"):
			self.create_room(user)
			return
		if(mode=="get_command"):
			self.get_command()
			return
		if(mode=="delete"):
			self.close_room(user)
			return
		if(mode=="tool"):
			self.tool(user)
			return
		
		#ポータル
		self.show_portal(user)
