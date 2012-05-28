#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ランキング
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db

class Ranking(db.Model):
	thread_list = db.ListProperty(db.Key)
	ranking_list = db.ListProperty(db.Key)
	date = db.DateTimeProperty(auto_now=True)
	
	def reset(self):
		self.thread_list=[]
	
	def add_rank(self,thread):
		if(not self.thread_list):
			self.thread_list=[]
		n=1000
		content_len=len(self.thread_list)
		while(content_len>=n):
			self.thread_list.pop(0)
			content_len=content_len-1
		self.thread_list.append(thread.key())
		self.put()
	
	def create_rank(self):
		rank={}
		for thread in self.thread_list:
			if(rank.has_key(thread)):
				rank[thread]=rank[thread]+1
			else:
				rank[thread]=1

		self.ranking_list=[]
		for k, v in sorted(rank.items(), key=lambda x:x[1], reverse=True):
			self.ranking_list.append(k)
		
		self.put()

	def get_rank(self,offset,limit):
		if(not self.ranking_list):
			return []
		return self.ranking_list[offset:offset+limit]
