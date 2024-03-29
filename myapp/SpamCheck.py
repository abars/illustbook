#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スパム判定
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import re
import logging

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
			Alert.alert_msg_with_write(self,"管理者権限が必要です。");
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
		
		Alert.alert_msg_with_write(self,"<H2>SPAM CHECKER</H2><H3>CHECK CODE</H3>"+form+"<H3>SPAM LIST</H3>"+ret+"<BR><BR><A HREF='./spam_delete'>DELETE ALL</A>")		

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
	def is_ascii(string):
		if string:
			return max([ord(char) for char in string]) < 128
		return True

	@staticmethod
	def _get_link_count(content):
		p = re.compile(r'http')
		list=p.split(content)
		http_link_count=len(list)

		p = re.compile(r'www\.')
		list=p.split(content)
		www_link_count=len(list)

		return max(http_link_count,www_link_count)

	@staticmethod
	def check(content,checkcode):
		link_count=SpamCheck._get_link_count(content)
		if(link_count>=5):
			return True;
		if(link_count>=2 and SpamCheck.is_ascii(content)):
			return True
		if(re.search(checkcode,content)):
			return True;
		if(re.search("viagra",content)):
			return True;
		if(re.search("taobaosonic",content)):
			return True;
		if(re.search(u"タオバオ",content) and re.search(u"代行",content)):
			return True;
		if(re.search(u"精力剤",content)):
			return True;
		if(re.search(u"死ね",content)):
			return True
		if(re.search(u"キモい",content)):
			return True
		if(re.search(u"www2\.tbb\.t-com\.ne\.jp/hapine/",content)):
			return True
		return False;
	
	@staticmethod
	def get_check_code():
		checkcode=memcache.get("spamcheck")
		if checkcode is None:
			checkcode="	no check code exist"
		if(len(checkcode)<8):
			checkcode="	no check code exist"
		return checkcode

	@staticmethod
	def is_spam_ip(remote_host,user):
		#if(user):
		#	return False
		#if(remote_host):
		#	if(re.search("ap\.yournet\.ne\.jp",remote_host)):
		#		logging.error("Spam host detected "+remote_host)
		#		return True
		return False

	@staticmethod
	def is_deny_host(remote_host,deny_host_list):
		if(not deny_host_list):
			return False
		host_list=deny_host_list.split(",")
		for host in host_list:
			if(host==""):
				continue
			try:
				if(re.search(host,remote_host)):
					logging.error("Spam host detected "+remote_host)
					return True
			except:
				logging.error("Deny host exception detected host:"+host+" remote_host:"+remote_host)
		return False

	@staticmethod
	def check_all(req,content,remote_host,user,bbs,is_flash,is_english):
		checkcode=SpamCheck.get_check_code()
		spam_host=SpamCheck.is_spam_ip(remote_host,user)
		if(not spam_host):
			spam_host=SpamCheck.is_deny_host(remote_host,bbs.deny_host_list)
		if(SpamCheck.check(content,checkcode) or spam_host):
			if(spam_host):
				if(is_english):
					spam_mes=BbsConst.SPAM_HOST_CHECKED_ENGLISH+remote_host
				else:
					spam_mes=BbsConst.SPAM_HOST_CHECKED+remote_host
			else:
				if(is_english):
					spam_mes=BbsConst.SPAM_CHECKED_ENGLISH
				else:
					spam_mes=BbsConst.SPAM_CHECKED
			req.write_status(is_flash,spam_mes)
			return True
		return False

	@staticmethod
	def is_deny(req):
		if re.search("webmeup\-crawler",req.headers.get('User-Agent')):
			return True
		if re.search("opensiteexplorer",req.headers.get('User-Agent')):
			return True
		if re.search("AhrefsBot",req.headers.get('User-Agent')):
			return True
		if re.search("SemrushBot",req.headers.get('User-Agent')):
			return True
		if re.search("Linespider",req.headers.get('User-Agent')):
			return True
		if re.search("GrapeshotCrawler",req.headers.get('User-Agent')):
			return True
		return False






