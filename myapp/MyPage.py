#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#マイページ、ソーシャル風
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import logging

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

import template_select

from myapp.Analyze import Analyze
from myapp.Bbs import Bbs
from myapp.Entry import Entry
from myapp.Counter import Counter
from myapp.Response import Response
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.ThreadImage import ThreadImage

from myapp.SetUtf8 import SetUtf8
from myapp.RecentCommentCache import RecentCommentCache
from myapp.MappingId import MappingId
from myapp.SpamCheck import SpamCheck
from myapp.SpamDelete import SpamDelete
from myapp.AddNewThread import AddNewThread
from myapp.Alert import Alert
from myapp.OwnerCheck import OwnerCheck
from myapp.UpdateBbs import UpdateBbs
from myapp.AddEntry import AddEntry
from myapp.Admin import Admin
from myapp.PageGenerate import PageGenerate
from myapp.Applause import Applause
from myapp.RssFeed import RssFeed
from myapp.ShowThread import ShowThread
from myapp.ShowBbs import ShowBbs
from myapp.MoveAccount import MoveAccount
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.MoperUpload import MoperUpload
from myapp.MoperImportRaster import MoperImportRaster
from myapp.MoperGuide import MoperGuide
from myapp.MoperLoad import MoperLoad
from myapp.MoperPlayer import MoperPlayer
from myapp.MoperDraw import MoperDraw
from myapp.AnalyzeAccess import AnalyzeAccess
from myapp.CssDesign import CssDesign
from myapp.ImageFile import ImageFile
from myapp.UpdateThread import UpdateThread
from myapp.EditThread import EditThread
from myapp.ViolationTerms import ViolationTerms
from myapp.MappingThreadId import MappingThreadId
from myapp.DrawWindow import DrawWindow
from myapp.Bookmark import Bookmark
from myapp.AddBookmark import AddBookmark
from myapp.NicoTracker import NicoTracker
from myapp.UpdateProfile import UpdateProfile
from myapp.Alert import Alert
from myapp.StackFeedData import StackFeedData
from myapp.ApiObject import ApiObject
from myapp.OwnerCheck import OwnerCheck
from myapp.Ranking import Ranking
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.Pinterest import Pinterest

class MyPage(webapp.RequestHandler):
	def delete_user_thread(self,user_id):
		query=MesThread.all().filter("user_id =",user_id)
		thread_list=query.fetch(limit=1000)
		for thread in thread_list:
			thread.delete()

	def withdraw(self,bookmark,your_bbs_count):
		user_id=self.request.get("user_id")
		if(not user_id):
			Alert.alert_msg_with_write(self,"ユーザIDが必要です。")
			return True

		user=users.get_current_user()
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user_id)	#キャッシュから取得するのを防止
		if(not bookmark):
			Alert.alert_msg_with_write(self,"ユーザが見つかりません。")
			return True

		if(OwnerCheck.check_bookmark(bookmark,user)):
			Alert.alert_msg_with_write(self,"退会する権限がありません。")
			return True

		is_english=CssDesign.is_english(self)

		if(your_bbs_count==0):
			#delete_user_thread(user.user_id())	#他人の掲示板に描いたイラストは慎重に削除する必要がある気がする
			bookmark.delete()
			msg="退会が完了しました。"
			if(is_english):
				msg="Complete"
			Alert.alert_msg_with_write(self,msg);
		else:
			msg="退会する前にレンタルしている掲示板を削除する必要があります。<BR>掲示板の削除はマイページのイラストタブで編集を押すことで行うことができます。<BR>残りの掲示板数："+str(your_bbs_count)
			if(is_english):
				msg="You must delete your BBS before withdraw.<br/>You have "+str(your_bbs_count)+" BBS yet."
			Alert.alert_msg_with_write(self,msg)
			return True

		return True

	def get(self,regist_mode):
		SetUtf8.set()

		#表示モードかどうか
		view_mode=None
		if(self.request.get("user")):
			view_mode=self.request.get("user")
		
		#ユーザ検索
		if(self.request.get("user_id")):
			target_bookmark=ApiObject.get_bookmark_of_user_id(self.request.get("user_id"))
			if(target_bookmark==None):
				Alert.alert_msg_with_write(self,"ユーザが見つかりません。")
				return
			view_mode=str(target_bookmark.key());
		
		#リダイレクトURL
		host="http://"+MappingId.mapping_host(self.request.host)+"/";
		redirect_url=host+"mypage";
	
		#編集モードか
		edit_mode=0
		if(self.request.get("edit")):
			edit_mode=int(self.request.get("edit"))
	
		#掲示板一覧
		user = users.get_current_user()
		favorite=""
		bookmark=None

		#管理人かどうか
		is_admin=0
		if(OwnerCheck.is_admin(user)):# and self.request.get("is_admin")):
			is_admin=1

		#自分だったらビューモードにしない
		if(user and self.request.get("user_id")==user.user_id() and not self.request.get("withdraw")):
			view_mode=0
		
		#ログインしているか
		login_flag=0
		if(user):
			login_flag=1

		#表示設定
		if(view_mode):
			bookmark=db.get(view_mode)
		else:
			if user:
				bookmark=ApiObject.get_bookmark_of_user_id(user.user_id())
			else:
				bookmark=None

		#掲示板の新規作成が完了したか
		regist_finish=False
		if(regist_mode=="regist"):
			regist_finish=True
		
		#プロフィールを編集
		edit_profile=Pinterest.get_profile_for_edit(bookmark,view_mode)
		
		#アカウントの凍結
		if(self.request.get("freez") and is_admin):
			bookmark=ApiObject.get_bookmark_of_user_id_for_write(self.request.get("user_id"))
			bookmark.frozen=int(self.request.get("freez"))
			bookmark.put()
		
		#退会
		if(self.request.get("withdraw") and self.request.get("withdraw")=="go"):
			if(not bookmark):
				Alert.alert_msg_with_write(self,"ユーザ情報は未登録です。");
				return
			your_bbs_count=Bbs.all().filter("del_flag =",0).filter("user_id =",bookmark.user_id).count()
			if(self.withdraw(bookmark,your_bbs_count)):
				return;

		#リダイレクト
		if(BbsConst.PINTEREST_MODE):
			if((user and OwnerCheck.is_admin(user)) or BbsConst.PINTEREST_MODE==2):
				if(regist_finish):
					return Pinterest.get_core(self,Pinterest.PAGE_MODE_REGIST)
				else:
					return Pinterest.get_core(self,Pinterest.PAGE_MODE_MYPAGE)
		