#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板ごとのアクセス解析ログ(リファラの格納)
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db

class Analyze(db.Model):
	bbs_key =db.ReferenceProperty()
	ip = db.StringProperty(indexed=False)
	adr = db.StringListProperty(indexed=False)
	content = db.StringListProperty(indexed=False)
	date = db.DateTimeProperty(auto_now=True,indexed=False)
	
	def init_analyze(self,key):
		self.ip="0"
		self.bbs_key=key
	
	def reset(self):
		self.content=[]
		self.adr=[]
	
	@staticmethod
	def get_request_referer(request):
		if("Referer" in request.headers):
			if request.headers['Referer']:
				return request.headers['Referer']
		return ""
	
	def add_referer(self,referer,url,content_name):
		n=256
		
		#hot referer
		if(referer):
			adr_len=len(self.adr)
			while(adr_len>=n):
				self.adr.pop(0)
				adr_len=adr_len-1
			self.adr.append(referer)
		
		#hot entry
		if url:
			content_len=len(self.content)
			while(content_len>=n):
				self.content.pop(0)
				content_len=content_len-1
			self.content.append(content_name+"@"+url)
		
		#書き込み
		try:
			self.put()
		except:
			a=None
	
	def get_referer(self):
		ret=""
		for data in self.adr:
			ret+=data+"#"
		ret+="<>"
		for data in self.content:
			ret+=data+"#"
		return ret		
