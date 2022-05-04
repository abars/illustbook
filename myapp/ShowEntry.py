#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#コメントを表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Counter import Counter
from myapp.Alert import Alert
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Entry import Entry
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.CssDesign import CssDesign
from myapp.BbsConst import BbsConst
from myapp.MappingThreadId import MappingThreadId
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.CounterWorker import CounterWorker
from myapp.ApiObject import ApiObject

class ShowEntry(webapp.RequestHandler):
	@staticmethod
	def _get_response(com_list_,res_hash,thread,bbs):
		#コメントソート
		if(bbs.bbs_mode != BbsConst.BBS_MODE_NO_IMAGE):
		#if(thread.illust_mode):
			com_list_.reverse()
		
		#レスを取得
		com_list=[]
		for com in com_list_:
			res_list=[]
			for res in com.res_list:
				one_res=res_hash[res]
				res_list.append(one_res)
			image_key=None
			if(com.illust_reply):
				image_key=Entry.illust_reply_image_key.get_value_for_datastore(com)
			com_list.append({'com':com, 'image_key':image_key, 'res_list':res_list})
		return com_list
	
	#ユーザ名を取得
	@staticmethod
	def get_user_name(user):
		if(not user):
			return ""
		user_id=user.user_id()
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(not bookmark):
			return ""
		return bookmark.name

	#レスの取得
	@staticmethod
	def _get_entry_res(entry_list):
		res_id_list=[]

		if(type(entry_list)==dict):
			for com in entry_list:
				for res in entry_list[com].res_list:
					res_id_list.append(res)
		else:
			for com in entry_list:
				for res in com.res_list:
					res_id_list.append(res)

		return ApiObject.get_cached_object_hash(res_id_list)

	@staticmethod
	def _render_comment_core(req,host_url,bbs,thread,com_list_,edit_flag,bbs_key,logined,show_comment_form,is_admin,user_name,user,res_hash,show_ip):
		#レスを取得
		com_list=ShowEntry._get_response(com_list_,res_hash,thread,bbs)

		#コメントの編集を行うか
		comment_edit=req.request.get("comment_edit")

		#iPhoneかどうか
		is_iphone=CssDesign.is_iphone(req)

		#英語版かどうか
		is_english=CssDesign.is_english(req)
		
		#スパム対策
		force_login_to_create_new_image=BbsConst.FORCE_LOGIN_TO_CREATE_NEW_IMAGE
		force_login_to_create_new_comment=BbsConst.FORCE_LOGIN_TO_CREATE_NEW_COMMENT

		#レンダリング
		template_values = {
			'host': host_url,
			'bbs': bbs,
			'thread': thread,
			'com_list':com_list,
			'edit_flag':edit_flag,
			'bbs_key': bbs_key,
			'logined':logined,
			'show_comment_form':show_comment_form,
			'is_admin':is_admin,
			'user_name': user_name,
			'user': user,
			'redirect_url': req.request.path,
			'comment_edit': comment_edit,
			'is_iphone': is_iphone,
			'is_english': is_english,
			'show_ip': show_ip,
			'force_login_to_create_new_image': force_login_to_create_new_image,
			'force_login_to_create_new_comment': force_login_to_create_new_comment
			}

		path = "/html/thread/thread_comment.html"
		return template_select.render(path, template_values)

	#コメントを一つレンダリング
	@staticmethod
	def render_comment(req,host_url,bbs,thread,com_list_,edit_flag,bbs_key,logined,show_comment_form,is_admin,user_name,user,show_ip):
		res_hash=ShowEntry._get_entry_res(com_list_)
		return ShowEntry._render_comment_core(req,host_url,bbs,thread,com_list_,edit_flag,bbs_key,logined,show_comment_form,is_admin,user_name,user,res_hash,show_ip)

	#コメントをまとめてレンダリング
	@staticmethod
	def render_comment_list(req,all_threads_cached,host_url,bbs,show_comment_form,logined,is_admin,user_name,user):
		edit_flag=False
		show_ip=False
		
		bbs_key=bbs.key()

		#コメントとレスを先行して全て取得
		entry_key_list=[]
		for thread in all_threads_cached:
			if not thread:
				continue
			for entry in thread.cached_entry_key:
				entry_key_list.append(entry)
		entry_hash=ApiObject.get_cached_object_hash(entry_key_list)
		res_hash=ShowEntry._get_entry_res(entry_hash)

		#コメントをレンダリング
		for thread in all_threads_cached:
			if not thread:
				continue
			entry_list=[]
			for entry in thread.cached_entry_key:
				one_entry=entry_hash[entry]
				entry_list.append(one_entry)
			thread.cached_render_comment=ShowEntry._render_comment_core(req,host_url,bbs,thread,entry_list,edit_flag,bbs_key,logined,show_comment_form,is_admin,user_name,user,res_hash,show_ip)
		

