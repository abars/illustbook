#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板の管理人かどうかを確認する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from BbsConst import BbsConst
from google.appengine.api import users

class OwnerCheck:
	@staticmethod
	def check(bbs,user):
		if(not user):
			return 1
		if(not bbs):
			return 1
		if(bbs.official):
			return 1
		if(user.user_id()==bbs.user_id):
			return 0
		return 1
	
	@staticmethod
	def check_bookmark(bookmark,user):
		if(not user):
			return 1
		if(not bookmark):
			return 1
		if(users.is_current_user_admin()):
			return 0
		if(user.user_id()==bookmark.user_id):
			return 0
		return 1
	
	@staticmethod
	def is_admin(user):
		if(not user):
			return 0
		return users.is_current_user_admin()

