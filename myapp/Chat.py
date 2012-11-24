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

from myapp.Alert import Alert
from myapp.SetUtf8 import SetUtf8
from myapp.Bookmark import Bookmark
from myapp.CssDesign import CssDesign
from myapp.ChatRoom import ChatRoom
from myapp.ApiObject import ApiObject
from myapp.Bbs import Bbs
from myapp.OwnerCheck import OwnerCheck

class Chat(webapp.RequestHandler):
	#エラー定数
	ERROR_DISCONNECT=-2
	ERROR_NO_ROOM=-1

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
			Alert.alert_msg_with_write(self,"ルーム名は必須です。")
			return
		if(not user):
			Alert.alert_msg_with_write(self,"ルームの作成にはログインが必要です。")
			return

		user_name=self.get_user_name(user)

		canvas_size=self.request.get("canvas_size")
		size=canvas_size.split("x")
		canvas_width=int(size[0])
		canvas_height=int(size[1])

		room=ChatRoom()
		room.name=self.request.get("name")
		room.user_id=user.user_id()
		room.user_name=user_name
		room.command_list=""
		room.command_cnt=0
		room.user_count=0
		room.snap_range=0
		room.create_date=datetime.datetime.now()
		room.canvas_width=canvas_width
		room.canvas_height=canvas_height
		room.password=self.request.get("pass")
		room.is_always=0
		
		if(room.password=="always"):
			room.is_always=1
			room.password=""
		
		room.put()
		self.redirect("./chat")
	
	#ルームを終了する
	def close_room(self,user):
		try:
			room=db.get(self.request.get("key"))
		except:
			room=None
		if(not room):
			Alert.alert_msg_with_write(self,"ルームが見つかりません。")
			return
		if(not user or room.user_id!=user.user_id()):
			Alert.alert_msg_with_write(self,"終了する権限がありません。")
			return
		room.delete()
		self.redirect("./chat")
	
	#ルームにコマンドを送る
	def post_command(self):
		key=self.request.get("key")
		cmd_count=int(self.request.get("command_count"))
		user_count=int(self.request.get("user_count"))
		client_id=self.request.get("client_id")
		
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
			size=db.run_in_transaction(Chat.post_command_core,key,cmd_list,cmd_count,user_count,client_id)	#排他制御を行う
			if(size==Chat.ERROR_NO_ROOM):
				ApiObject.write_json_core(self,{"status":"not_found"})
			else:
				if(size==Chat.ERROR_DISCONNECT):
					ApiObject.write_json_core(self,{"status":"disconnect"})
				else:
					ApiObject.write_json_core(self,{"status":"success","size":size})
		except:
			ApiObject.write_json_core(self,{"status":"failed"})
	
	#スナップショットを作成
	def post_snapshot(self):
		key=self.request.get("key")
		snap_shot_0=self.request.get("snap_shot_0")
		snap_shot_1=self.request.get("snap_shot_1")
		thumbnail=self.request.get("thumbnail")
		snap_range=int(self.request.get("snap_range"))
		try:
			db.run_in_transaction(Chat.post_snapshot_core,key,snap_shot_0,snap_shot_1,snap_range,thumbnail)
			ApiObject.write_json_core(self,{"status":"success"})
		except:
			ApiObject.write_json_core(self,{"status":"failed"})

	@staticmethod
	def post_snapshot_core(key,snap_shot_0,snap_shot_1,snap_range,thumbnail):
		#スナップショットを格納
		room=db.get(key)
		
		#既にスナップショットが作成されている
		if(room.snap_range>=snap_range):
			return

		#サムネイルを格納
		room.thumbnail=db.Blob(base64.b64decode(thumbnail))

		#スナップショットまでのコマンドを消去
		server_command_list=room.command_list.split(" , ")
		new_command_list=""
		limit=room.command_cnt
		for i in range(snap_range,limit):
			cmd=server_command_list[i-room.snap_range]
			if(new_command_list==""):
				new_command_list=cmd
			else:
				new_command_list=new_command_list+" , "+cmd
		
		#スナップショットコマンドを追加
		room.command_list=new_command_list

		#スナップショットを格納
		room.snap_range=snap_range
		room.snap_shot_0=snap_shot_0
		room.snap_shot_1=snap_shot_1

		room.put()
	
	@staticmethod
	def post_command_core(key,cmd,cmd_count,user_count,client_id):
		room=db.get(key)
		if(room==None):
			return Chat.ERROR_NO_ROOM
		if(not(client_id in room.channel_client_list)):
			return Chat.ERROR_DISCONNECT

		if(user_count!=-1):
			room.user_count=user_count
		if(room.command_list==""):
			room.command_list=cmd
		else:
			room.command_list=room.command_list+" , "+cmd
		room.command_cnt=room.command_cnt+cmd_count
		room.put()

		for client in room.channel_client_list:
			channel.send_message( client , "update" )

		return sys.getsizeof(room.command_list)+sys.getsizeof(room)

	#スナップショットを取得する
	def get_snap_shot(self):
		room=db.get(str(self.request.get("key")))

		if(room==None):
			ApiObject.write_json_core(self,{"status":"failed"})
			return
			
		ApiObject.write_json_core(self,{"status":"success","snap_shot_0":room.snap_shot_0,"snap_shot_1":room.snap_shot_1,"snap_range":room.snap_range})
	
	#ユーザリストを取得する
	def get_user_list(self):
		room=db.get(str(self.request.get("key")))

		if(room==None):
			ApiObject.write_json_core(self,{"status":"failed"})
			return

		dic={}
		for client in room.channel_client_list:
			user_id=client.split("_")[0]
			name="unknown"
			bookmark=ApiObject.get_bookmark_of_user_id(user_id)
			if(bookmark):
				name=bookmark.name
			dic[client]=name
		
		ApiObject.write_json_core(self,{"status":"success","user_list":dic});

	#コマンドを取得する
	def get_command(self):
		room=db.get(str(self.request.get("key")))
		
		if(room==None):
			ApiObject.write_json_core(self,{"status":"not_found"})
			return

		client_id=self.request.get("client_id")
		if(not(client_id in room.channel_client_list)):
			ApiObject.write_json_core(self,{"status":"disconnect"})
			return

		offset=int(self.request.get("offset"))
		limit=int(self.request.get("limit"))
		
		now_len=room.command_cnt
		if (offset+limit)>now_len:
			limit=now_len-offset
		
		server_command_list=room.command_list.split(" , ")
		
		command_list=[]
		for i in range(offset,offset+limit):
			if(i<room.snap_range):
				cmd_nop=4
				nop_command="[{'cmd':"+str(cmd_nop)+"}]";
				command_list.append(nop_command)
			else:
				one_cmd=server_command_list[i-room.snap_range]
				command_list.append(one_cmd)
		
		ApiObject.write_json_core(self,{"status":"success","offset":offset,"count":limit,"command_list":command_list})
	
	#ポータル
	def show_portal(self,user):
		is_iphone=CssDesign.is_iphone(self)
		room_list=ChatRoom.all().order("-create_date").fetch(limit=100)
		
		show_room=[]
		for room in room_list:
			room.from_last_update=(Chat.get_sec(datetime.datetime.now())-Chat.get_sec(room.date))/60
			room.from_created=(Chat.get_sec(datetime.datetime.now())-Chat.get_sec(room.create_date))/60
			if(room.from_last_update>=10 and (not room.is_always)):
				room.delete()
			else:
				if(room.from_last_update>=1 and room.user_count>=1):
					room.user_count=0
				show_room.append(room)
		
		is_admin=False
		if(OwnerCheck.is_admin(user)):
			is_admin=True

		template_values = {
			'host': "./",
			'is_iphone': is_iphone,
			'user': user,
			'redirect_url': self.request.path,
			'mode': "chat",
			'header_enable': False,
			'room_list': show_room,
			'is_admin':is_admin
		}
		path = os.path.join(os.path.dirname(__file__), '../html/portal.html')
		self.response.out.write(template.render(path, template_values))
	
	#経過時間取得
	@staticmethod
	def get_sec(now):
		return int(time.mktime(now.timetuple()))
	
	#サムネイル取得
	def thumbnail(self):
		room=db.get(str(self.request.get("key")))
		if(not room) or (not room.thumbnail):
			self.redirect("./static_files/empty_user.png")
			return
		self.response.headers['Content-Type'] = "image/png"
		self.response.out.write(room.thumbnail)
		return
	
	@staticmethod
	def add_user(room_key,client_id):
		db.run_in_transaction(Chat.add_user_core,room_key,client_id)
		room=db.get(room_key)
		Chat.user_update_notify(room)

	@staticmethod
	def add_user_core(room_key,client_id):
		room=db.get(room_key)

		#ユーザの追加
		if(not room.channel_client_list):
			room.channel_client_list=[]	#ログイン中
		if(not room.channel_client_list_for_reconnect):
			room.channel_client_list_for_reconnect=[]	#再接続
		room.channel_client_list.append(client_id)
		room.channel_client_list_for_reconnect.append(client_id)

		#ユーザ数を変更
		room.user_count=len(room.channel_client_list)
		room.put()

	@staticmethod
	def remove_user(room_key,client_id):
		db.run_in_transaction(Chat.remove_user_core,room_key,client_id)
		room=db.get(room_key)
		Chat.user_update_notify(room)

	@staticmethod
	def remove_user_core(room_key,client_id):
		room=db.get(room_key)

		#対象者を削除
		room.channel_client_list.remove(client_id)

		#2時間経過したユーザも削除（トークンの有効期限が2時間なので）
		server_time=Chat.get_sec(datetime.datetime.now())
		for one_user in room.channel_client_list:
			past=server_time-int(one_user.split("_")[1])
			if(past>=60*60*2):
				room.channel_client_list.remove(one_user)
				logging.info("### timeout user "+str(past)+"[sec]")

		#ユーザ数を変更
		room.user_count=len(room.channel_client_list)

		room.put()

	@staticmethod
	def user_update_notify(room):
		for client in room.channel_client_list:
			channel.send_message( client , "update_user" )

	#チャットツール
	def tool(self,user):
		bbs=None
		bbs_key=""
		thread_key=""

		if(self.request.get("key")=="always"):
			try:
				room_key=ChatRoom.all().filter("is_always =",1).fetch(1)[0].key()
			except:
				room_key=None
		else:
			room_key=self.request.get("key")
		if(not room_key):
			Alert.alert_msg_with_write(self,"ルームキーが必要です。")
			return

		ipad=CssDesign.is_tablet(self)
		viewmode=self.request.get("viewmode")
		password=self.request.get("pass")

		try:
			room=db.get(room_key)
		except:
			room=None

		alert_footer="<BR><A HREF='./chat'><IMG SRC='./static_files/chat/logo.png'/></A>"

		login_message=""
		if(not user):
			login_url=users.create_login_url(self.request.url)
			login_message="<BR><A HREF='"+login_url+"' class='g-button'>Googleアカウントでログイン</A><BR>"

		if(not room):
			Alert.alert_msg_with_write(self,"このチャットルームは終了されています。"+alert_footer)
			return
		
		if(room.password and room.password!=password):
			Alert.alert_msg_with_write(self,"チャットルームのパスワードが一致しません。"+alert_footer)
			return
		
		if(not user):
			Alert.alert_msg_with_write(self,"チャットルームへの参加にはログインが必要です。<BR>"+login_message+alert_footer)
			return

		canvas_width=room.canvas_width
		canvas_height=room.canvas_height

		user_id=user.user_id()
		user_name=self.get_user_name(user)
		server_time=Chat.get_sec(datetime.datetime.now())
		
		bbs_list=Bbs.all().filter("user_id =",user.user_id()).filter("del_flag =",0).fetch(limit=10)

		client_id=str(user.user_id()) + "_"+ str(server_time)
		token = channel.create_channel(client_id)

		#排他制御が必要
		Chat.add_user(room_key,client_id)

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
		'server_time':server_time,
		'bbs_list':bbs_list,
		'logined':True,
		'viewmode':viewmode,
		'room_name':room.name,
		'token':token,
		'client_id':client_id
		}
		
		path = os.path.join(os.path.dirname(__file__), '../html/tools/draw_window_ipad.htm')
		self.response.out.write(template.render(path, template_values))
	
	#インタフェース
	def post(self):
		mode=self.request.get("mode")
		if(mode=="post_command"):
			self.post_command()
			return
		if(mode=="post_snapshot"):
			self.post_snapshot()
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
		if(mode=="thumbnail"):
			self.thumbnail()
			return
		if(mode=="snap_shot"):
			self.get_snap_shot()
			return
		if(mode=="user_list"):
			self.get_user_list()
			return
		
		#ポータル
		self.show_portal(user)
