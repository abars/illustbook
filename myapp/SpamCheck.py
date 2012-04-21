#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スパム判定
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import re

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from myapp.SetUtf8 import SetUtf8;
from myapp.BbsConst import BbsConst;
from myapp.Alert import Alert
from myapp.Entry import Entry
from myapp.MesThread import MesThread
from myapp.OwnerCheck import OwnerCheck

class SpamCheck(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		user = users.get_current_user()

		is_admin=0
		if(user):
			if(OwnerCheck.is_admin(user)):
				is_admin=1
		
		if(not is_admin):
			self.response.out.write(Alert.alert_msg("管理者権限が必要です。",self.request.host));
			return
		
		message=""
		new_code=self.request.get('code')
		if(new_code):
			if(len(new_code)>=8):		
				memcache.set("spamcheck",new_code)
				message="updated check code to "+new_code
			else:
				message="too short check code"

		checkcode=SpamCheck.get_check_code()

		query=Entry.all()
		thread=None
		try:
			thread=db.get(checkcode)
		except:
			thread=None
		if(thread):
			query.filter("thread_key =",thread)
		entrys=query.fetch(limit=1000)

		ret=""
		spam_detected=0
		for entry in entrys:
			if(SpamCheck.check_with_thread(entry,checkcode)):
				ret+=entry.content+"<BR>"
				spam_detected=1
		if(not spam_detected):
			ret="SpamNotFound"
		
		form="code:"+checkcode+"<BR>"+message+"<BR>"
		form+="<form method='GET' action='spam_check'>thread_key:<input type='text' name='code' size=40><input type='submit' value='UPDATE'></form>";
		
		self.response.out.write(Alert.alert_msg("<H2>SPAM CHECKER</H2><H3>CHECK CODE</H3>"+form+"<H3>SPAM LIST</H3>"+ret+"<BR><BR><A HREF='./spam_delete'>DELETE ALL</A>",self.request.host))		

	@staticmethod
	def check_with_thread(entry,checkcode):
		is_spam=0
		if(SpamCheck.check(entry.content,checkcode)):
			is_spam=1
		try:
			if(entry.thread_key and str(entry.thread_key.key())==checkcode):
				is_spam=1
		except:
			is_spam=0
		return is_spam

	@staticmethod
	def check(content,checkcode):
		p = re.compile(r'http')
		list=p.split(content)
		if(len(list)>=5):
			return True;		
		if(re.search(checkcode,content)):
			return True;
		if(re.search("viagra",content)):
			return True;
		return False;		
	
	@staticmethod
	def get_check_code():
		checkcode=memcache.get("spamcheck")
		if checkcode is None:
			checkcode="	no check code exist"
		if(len(checkcode)<8):
			checkcode="	no check code exist"
		return checkcode
