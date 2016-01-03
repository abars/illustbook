#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#チャットルーム
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.Analyze import Analyze
from myapp.Counter import Counter
from myapp.BbsConst import BbsConst
from myapp.AppCode import AppCode

import pickle
import StringIO
import logging
import datetime

class ChatChunk(db.Model): 
	data = db.BlobProperty() 
	index = db.IntegerProperty()
	date = db.DateTimeProperty()

class ChatRoom(db.Model):
	name = db.StringProperty(indexed=False)
	password = db.StringProperty(indexed=False)
	user_id = db.StringProperty()	#Owner
	user_name = db.StringProperty()
	user_count = db.IntegerProperty()
	command_list = db.TextProperty(indexed=False)
	command_cnt = db.IntegerProperty(indexed=False)
	from_last_update = db.IntegerProperty()
	from_created = db.IntegerProperty()
	thumbnail=db.BlobProperty(indexed=False)
	snap_shot_0=db.TextProperty(indexed=False)
	snap_shot_1=db.TextProperty(indexed=False)
	snap_range=db.IntegerProperty(indexed=False)
	canvas_width=db.IntegerProperty(indexed=False)
	canvas_height=db.IntegerProperty(indexed=False)
	channel_client_list=db.StringListProperty()
	channel_client_list_for_reconnect=db.StringListProperty()
	heart_beat_blob=db.BlobProperty()
	is_always=db.IntegerProperty()	#for always room search
	create_date = db.DateTimeProperty(auto_now=False)
	date = db.DateTimeProperty()
	sand = db.StringProperty()

	chunk_list = db.ListProperty(db.Key)
	chunk_cnt = db.IntegerProperty()

	heart_beat = {}

	def delete(self):
		for chunk in self.chunk_list:
			try:
				db.delete(db.get(chunk))
			except:
				ok=True
		db.Model.delete(self)
	
	def put(self):
		chunk_size = 500000	#500KBで分割する

		self.date=datetime.datetime.now()

		cnt=0
		if(self.command_list!=""):
			data=db.Blob(pickle.dumps(self.command_list))
			cnt = int(len(data)/chunk_size)+1
			for i in xrange(cnt):
				chunk_data = data[i*chunk_size:(i+1)*chunk_size]

				if(i<len(self.chunk_list)):
					chunk=db.get(self.chunk_list[i])
					chunk.data=chunk_data
					chunk.date=self.date
					chunk.put()
				else:
					chunk = ChatChunk(parent=self)
					chunk.data=chunk_data
					chunk.index=i;
					chunk.date=self.date
					chunk.put()
					self.chunk_list.append(db.Key(str(chunk.key())))

		self.command_list=""
		self.chunk_cnt=cnt

		self.heart_beat_blob=db.Blob(pickle.dumps(self.heart_beat))

		db.Model.put(self)
	
	def download(self):
		cnt=self.chunk_cnt
		if(cnt==0):
			self.command_list=""
		else:
			data=StringIO.StringIO()
			for i in xrange(cnt):
				chunk=self.chunk_list[i]
				chunk_data=db.get(chunk)
				if(chunk_data.date!=self.date):
					raise Exception,"chunk missmatch" 
				chunk_data=chunk_data.data
				data.write(chunk_data)
			self.command_list=pickle.loads(data.getvalue())

		self.heart_beat=pickle.loads(self.heart_beat_blob)
		
	@staticmethod
	def get(key):
		room=db.get(key)
		if(not room):
			return None
		room.download()
		return room
