#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#メイン関数とポータル関係
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

from google.appengine.ext import webapp

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

webapp.template.register_template_library('templatetags.django_filter')

#-----------------------------------------------------------------
#DB
#-----------------------------------------------------------------

from Analyze import Analyze
from Bbs import Bbs
from Entry import Entry
from Counter import Counter
from Response import Response
from MesThread import MesThread
from BbsConst import BbsConst
from ThreadImage import ThreadImage

from SetUtf8 import SetUtf8
from RecentCommentCache import RecentCommentCache
from MappingId import MappingId
from SpamCheck import SpamCheck
from SpamDelete import SpamDelete
from AddNewThread import AddNewThread
from Alert import Alert
from OwnerCheck import OwnerCheck
from UpdateBbs import UpdateBbs
from AddEntry import AddEntry
from Admin import Admin
from AddNewBbs import AddNewBbs
from PageGenerate import PageGenerate
from SearchUser import SearchUser
from Applause import Applause
from RssFeed import RssFeed
from ShowThread import ShowThread
from ShowBbs import ShowBbs
from MoveAccount import MoveAccount
from MaintenanceCheck import MaintenanceCheck
from MoperUpload import MoperUpload
from MoperImportRaster import MoperImportRaster
from MoperGuide import MoperGuide
from MoperLoad import MoperLoad
from MoperPlayer import MoperPlayer
from MoperDraw import MoperDraw
from LocalToolDraw import LocalToolDraw
from LocalTool import LocalTool
from Embedded import Embedded
from AnalyzeAccess import AnalyzeAccess
from CssDesign import CssDesign
from ImageFile import ImageFile
from AddRes import AddRes
from UpdateThread import UpdateThread
from EditThread import EditThread
from ViolationTerms import ViolationTerms
from MappingThreadId import MappingThreadId
from DrawWindow import DrawWindow
from AddTag import AddTag
from SearchTag import SearchTag
from Bookmark import Bookmark
from AddBookmark import AddBookmark
from NicoTracker import NicoTracker
from UpdateProfile import UpdateProfile
from MyPage import MyPage
from ShowBookmark import ShowBookmark
from Comic import Comic
from AppPortal import AppPortal
from ApiUser import ApiUser
from ApiBookmark import ApiBookmark
from ApiFeed import ApiFeed
from ApiJs import ApiJs
from DevPortal import DevPortal
from SchemeUpdate import SchemeUpdate
from ApiPerpetuation import ApiPerpetuation
from EditBbs import EditBbs
from AppImage import AppImage
from SiteAnalyzer import SiteAnalyzer
from StackFeed import StackFeed
from StackFeedTweet import StackFeedTweet
from ApiObject import ApiObject
from CounterWorker import CounterWorker
from ShowIcon import ShowIcon

#-----------------------------------------------------------------
#ポータル
#-----------------------------------------------------------------

class MainPage(webapp.RequestHandler):
	def get(self):
		#移動
		if(self.request.host=="illust-book.appspot.com"):
			self.redirect(str("http://www.illustbook.net/"))
			return
	
		SetUtf8.set()
		
		#メンテナンス画面
		is_maintenance=0
		if(MaintenanceCheck.is_appengine_maintenance()):
			is_maintenance=1
		
		#BBS COUNT
		bbs_n=memcache.get("top_bbs_n")
		illust_n=memcache.get("top_illust_n")
		if(bbs_n is None or illust_n is None):
			cache=SiteAnalyzer.get_cache()
			bbs_n=cache.bbs_n
			illust_n=cache.illust_n
			memcache.set("top_bbs_n",bbs_n,60*60*12)
			memcache.set("top_illust_n",illust_n,60*60*12)
		
		#最近のタグ
		tag_list=SearchTag.get_recent_tag()
		
		#デベロッパーオプション
		user = users.get_current_user()
		is_dev_enable=OwnerCheck.is_admin(user)

		#iPhoneモードかどうか
		is_iphone=CssDesign.is_iphone(self)
		
		#URL生成
		template_values = {
			'host': "./",
			'mes_bord_url': 'mes_bord',
			'new_url': 'create_new_thread',
			'bbs_n':bbs_n,
			'illust_n':illust_n,
			'tag_list':tag_list,
			'is_dev_enable':is_dev_enable,
			'is_maintenance': is_maintenance,
			'is_iphone': is_iphone,
			'user': user,
			'redirect_url': self.request.path
		}

		#if(self.request.get("mode")=="family"):
		#	path = os.path.join(os.path.dirname(__file__), 'portal/family_index.html')
		#else:
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_index.html')
		self.response.out.write(template.render(path, template_values))

class Questionnaire(webapp.RequestHandler):
	def get(self):
		template_values = {
			'host' : './',
			'user': users.get_current_user(),
			'redirect_url': self.request.path
		}
		#if(self.request.get("mode")=="family"):
		#	path = os.path.join(os.path.dirname(__file__), 'portal/family_questionnaire.html')
		#else:
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_questionnaire.html')
		self.response.out.write(template.render(path, template_values))
		
class Profile(webapp.RequestHandler):
	def get(self):
		template_values = {
			'host': "./",
			'user': users.get_current_user(),
			'redirect_url': self.request.path
		}
		#if(self.request.get("mode")=="family"):
		#	path = os.path.join(os.path.dirname(__file__), 'portal/family_profile.html')
		#else:
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_profile.html')
		self.response.out.write(template.render(path, template_values))

class Support(webapp.RequestHandler):
	def get(self):
		template_values = {
			'host': "./",
			'user': users.get_current_user(),
			'redirect_url': self.request.path
		}
		#if(self.request.get("mode")=="family"):
		#	path = os.path.join(os.path.dirname(__file__), 'portal/family_support.html')
		#else:
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_support.html')
		self.response.out.write(template.render(path, template_values))

class Terms(webapp.RequestHandler):
	def get(self):

		#iPhoneモードかどうか
		is_iphone=CssDesign.is_iphone(self)

		template_values = {
			'host': "./",
			'is_iphone': is_iphone,
			'user': users.get_current_user(),
			'redirect_url': self.request.path
		}
		#if(self.request.get("mode")=="family"):
		#	path = os.path.join(os.path.dirname(__file__), 'portal/family_terms.html')
		#else:
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_terms.html')
		self.response.out.write(template.render(path, template_values))

class Community(webapp.RequestHandler):
	def get(self):
		new_mode=False
		if(self.request.get("new")):
			new_mode=True
		template_values = {
			'host': "./",
			'new': new_mode,
			'user': users.get_current_user(),
			'redirect_url': self.request.path
		}
		#if(self.request.get("mode")=="family"):
		#	path = os.path.join(os.path.dirname(__file__), 'portal/family_community.html')
		#else:
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_community.html')
		self.response.out.write(template.render(path, template_values))

class GuidePage(webapp.RequestHandler):
	def get(self):
		template_values = {
			'host': "./",
			'user': users.get_current_user(),
			'redirect_url': self.request.path
		}
		#if(self.request.get("mode")=="family"):
		#	path = os.path.join(os.path.dirname(__file__), 'portal/family_guide.html')
		#else:
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_guide.html')
		self.response.out.write(template.render(path, template_values))

class LinkPage(webapp.RequestHandler):
	def get(self):
		news=""
		
		#iPhoneモードかどうか
		is_iphone=CssDesign.is_iphone(self)
	
		template_values = {
			'host': './',
			'news': news,
			'is_iphone': is_iphone,
			'user': users.get_current_user(),
			'redirect_url': self.request.path
		}
		#if(self.request.get("mode")=="family"):
		#	path = os.path.join(os.path.dirname(__file__), 'portal/family_link.html')
		#else:
		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_link.html')
		self.response.out.write(template.render(path, template_values))

#-----------------------------------------------------------------
#削除系
#-----------------------------------------------------------------

#class Image (webapp.RequestHandler):
#	def get(self):
#		try:
#			entry = db.get(self.request.get("img_id"))
#		except:
#			entry=None
#		if(entry==None):
#			self.error(404)
#			return
#		if entry.image:
#			if(entry.illust_mode==4) :
#				self.response.headers['Content-Type'] = "image/png"
#			else:
#				self.response.headers['Content-Type'] = "image/jpeg"
#			self.response.out.write(entry.image)
#		else:
#			self.error(404)

class DelBbs(webapp.RequestHandler):
	def get(self):
		bbs=None
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			bbs=None
		if(bbs==None):
			self.response.out.write(Alert.alert_msg("削除対象が見つかりません。",self.request.host))
			return
		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			self.response.out.write(Alert.alert_msg("削除する権限がありません。",self.request.host))
			return
		bbs.del_flag=1
		bbs.put()
		self.redirect(str('./mypage'))

class VisibilityChangeEntry(webapp.RequestHandler):
	def get(self):
		bbs = db.get(self.request.get("bbs_key"))
		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			return
		entry = db.get(self.request.get("entry_key"))
		if(entry.hidden_flag):
			entry.hidden_flag = 0
		else:
			entry.hidden_flag = 1
		entry.put()

		thread = db.get(self.request.get("thread_key"))
		url=MappingThreadId.get_thread_url("./",bbs,thread)
		self.redirect(str(url))

class DelEn(webapp.RequestHandler):
	def get(self):
		bbs = db.get(self.request.get("bbs_key"))
		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			return
		entry = db.get(self.request.get("entry_key"))
		entry.del_flag = 0
		entry.put()
		#thread_key
		thread = db.get(self.request.get("thread_key"))
		thread.comment_cnt=thread.comment_cnt-1
		#thread.thread_entry_list.append(entry.key())
		thread.put()

		url=MappingThreadId.get_thread_url("./",bbs,thread)
		self.redirect(str(url))

		RecentCommentCache.invalidate(bbs)

class DelRes(webapp.RequestHandler):
	def get(self):
		entry = db.get(self.request.get("entry_key"))
		res= db.get(self.request.get("res_key"))

		thread_key=entry.thread_key
		bbs_key=thread_key.bbs_key

		user = users.get_current_user()
		if(OwnerCheck.check(bbs_key,user)):
			return

		res.delete()
		idx = entry.res_list.index(db.Key(self.request.get("res_key")))
		entry.res_list.pop(idx)
		entry.put()

		url=MappingThreadId.get_thread_url("./",bbs_key,thread_key)
		self.redirect(str(url))
		
		thread = db.get(str(thread_key.key()))
		thread.comment_cnt=thread.comment_cnt-1
		thread.put()


class DelThread(webapp.RequestHandler):
	def get(self):
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			bbs=None
		try:
			thread = db.get(self.request.get("thread_key"))
		except:
			thread=None
		
		if(not bbs or not thread):
			self.response.out.write(Alert.alert_msg("削除対象が見つかりません。",self.request.host))
			return
		
		del_ok=0		
		if(self.request.get("del_key")):
			if(thread.delete_key):
				if(thread.delete_key==self.request.get("del_key")):
					del_ok=1
				else:
					self.response.out.write(Alert.alert_msg("削除キーが一致しません。",self.request.host))
					return;					
		
		user = users.get_current_user()
		if(del_ok==0):
			if(OwnerCheck.check(bbs,user)):
				return

		thread.delete()

		url=MappingId.get_usr_url("./",bbs)
		self.redirect(str(url))

#class UploadImage(webapp.RequestHandler):
#	def post(self):
#		self.response.headers ['Content-type'] = "text/html;charset=utf-8"  
#		bbs = db.get(self.request.get("bbs_key"))
#		user = users.get_current_user()
#
#		if(bbs.bbs_mode==BbsConst.BBS_MODE_ONLY_ADMIN):
#			if(OwnerCheck.check(bbs,user)):
#				self.response.out.write("[error]")
#				return
#		try:
#			timage=ThreadImage()
#			timage.bbs_key=db.get(self.request.get("bbs_key"))
#			timage.image=db.Blob(self.request.body)			
#			timage.illust_mode=1
#			timage.put()
#			self.response.out.write(str(timage.key()))
#		except:
#			self.response.out.write("[error]")


#class UploadThumbnail(webapp.RequestHandler):
#	def post(self):
#		self.response.headers ['Content-type'] = "text/html;charset=utf-8"  

#		#self.response.out.write("[error]")
#		#return

#		try:
#			timage=db.get(self.request.get("image_key"))
#			timage.thumbnail=db.Blob(self.request.body)
#			timage.put()
#			self.response.out.write(str(timage.key()))
#		except:
#			self.response.out.write("[error]")
			
#class RealImage(webapp.RequestHandler):
#	def get(self):
#		try:
#			entry = db.get(self.request.get("img_id"))
#		except:
#			entry=None
#		if(entry==None):
#			self.error(404)
#			return
#		
#		template_values = {
#			'blog': entry,
#			'url': 'edit',
#			'url_linktext': 'edit blogs',
#			}
#
#		path = os.path.join(os.path.dirname(__file__), 'html/mes_image.html')
#		self.response.out.write(template.render(path, template_values))

class CheckId(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()
		short=self.request.get('id')
		if(MappingId.key_format_check(short)):
			self.response.out.write(Alert.alert_msg("IDは半角英数である必要があります。",self.request.host))
			return
		if(MappingId.check_capability(short,"")==0):
			self.response.out.write(Alert.alert_msg("ID:"+short+"は既に登録されていて利用できません。",self.request.host))
			return
		self.response.out.write(Alert.alert_msg("ID:"+short+"は利用可能です。",self.request.host))

#-----------------------------------------------------------------
#リダイレクト
#-----------------------------------------------------------------

class RedirectThread(webapp.RequestHandler):
	def get(self):
		try:
			bbs=db.get(self.request.get("bbs_key"))
		except:
			bbs=None
		if(bbs==None):
			self.response.out.write(Alert.alert_msg_notfound(self.request.host))
			return
		host_name=self.request.host
		if(host_name=="http://www.illust-book.appspot.com/"):
			host_name="http://www.illustbook.net/";		
		host_url="http://"+MappingId.mapping_host(host_name)+"/";
		url=MappingId.get_usr_url(host_url,bbs)
		self.redirect(str(url+self.request.get("thread_key")+".html"))

class RedirectBbs(webapp.RequestHandler):
	def get(self):
		try:
			bbs=db.get(self.request.get("bbs_key"))
		except:
			bbs=None
		if(bbs==None):
			self.response.out.write(Alert.alert_msg_notfound(self.request.host))
			return			
		host_name=self.request.host
		if(host_name=="http://www.illust-book.appspot.com/"):
			host_name="http://www.illustbook.net/";		
		host_url="http://"+MappingId.mapping_host(host_name)+"/";
		url=MappingId.get_usr_url(host_url,bbs)
		self.redirect(str(url))

application = webapp.WSGIApplication(
																			[('/', MainPage),
																			(r'/usr/(.*)/(.*)\.html',ShowThread),
																			(r'/usr/(.*)/',ShowBbs),
																			(r'/usr/(.*)/index.xml',RssFeed),
																			(r'/(.*)/(.*)\.html',ShowThread),
																			(r'/(.*)/',ShowBbs),
																			(r'/(.*)/index.xml',RssFeed),
																			('/guide', GuidePage),
																			('/bbs_index', RedirectBbs),
#																			('/img', Image),
																			(r'/css/(.*)\.(css)',CssDesign), 
																			(r'/css/(.*)\.(key)',CssDesign), 
#																			('/image', RealImage),
																			(r'/(img)/(.*)\.(jpg)',ImageFile), 
																			(r'/(img)/(.*)\.(png)',ImageFile), 
																			(r'/(img)/(.*)\.(txt)',ImageFile), 
																			('/(thumbnail)/([^\.]*)\.(jpg)', ImageFile),
																			('/(thumbnail)/([^\.]*)\.(gif)', ImageFile),
																			('/(thumbnail)/([^\.]*)\.(png)', ImageFile),
																			('/add_thread', AddNewThread),
																			('/add_bbs', AddNewBbs),
																			('/show_thread', RedirectThread),
																			('/add_entry', AddEntry),
																			('/del_ent', DelEn),
																			('/vis_ent', VisibilityChangeEntry),
																			('/del_bbs', DelBbs),
#																			('/upl_img', UploadImage),
#																			('/upl_thumbnail', UploadThumbnail),
																			('/upl_all', AddNewThread),
																			('/draw', DrawWindow),
																			('/draw_beta', DrawWindow),
																			('/del_thread', DelThread),
																			('/edit_bbs', EditBbs),
																			('/update_bbs', UpdateBbs),
																			('/edit_thread', EditThread),
																			('/update_thread', UpdateThread),
																			('/add_res', AddRes),
																			('/add_tag', AddTag),
																			('/del_res', DelRes),
																			('/add_bookmark', AddBookmark),
																			('/(mypage)',MyPage),
																			('/(regist)',MyPage),
																			('/ajax_ranking_update',SiteAnalyzer),
																			('/applause',Applause),
																			('/analyze',AnalyzeAccess),
																			('/check_id',CheckId),
																			('/embedded',Embedded),
																			('/draw_moper',MoperDraw),
																			('/upload_moper',MoperUpload),
																			('/moper_load',MoperLoad),
																			('/moper_player',MoperPlayer),
																			('/moper_import_raster',MoperImportRaster),
																			('/moper_guide',MoperGuide),
																			('/link',LinkPage),
																			('/spam_check',SpamCheck),
																			('/spam_delete',SpamDelete),
																			('/admin',Admin),
																			('/localtool',LocalTool),
																			('/localtool_draw',LocalToolDraw),
																			('/questionnaire',Questionnaire),
																			('/community',Community),
																			('/profile',Profile),
																			('/support',Support),
																			('/terms',Terms),
																			('/search',SearchUser),
																			('/search_tag',SearchTag),
																			('/move_account',MoveAccount),
																			('/violation',ViolationTerms),
																			('/nico_tracker',NicoTracker),
																			('/update_profile',UpdateProfile),
																			('/show_bookmark',ShowBookmark),
																			('/show_icon',ShowIcon),
																			('/comic',Comic),
																			('/scheme_update',SchemeUpdate),
																			('/app',AppPortal),
																			('/app/(.*)/img/(.*)',AppImage),
																			('/api_feed',ApiFeed),
																			('/api_user',ApiUser),
																			('/api_bookmark',ApiBookmark),
																			('/api_perpetuation',ApiPerpetuation),
																			('/api_js',ApiJs),
																			('/dev',DevPortal),
																			('/stack_feed_worker',StackFeed),
																			('/counter_worker',CounterWorker),
																			('/feed_tweet',StackFeedTweet)
																			],
																		 	debug=False)
																			
#for python2.5
#def main():
#	run_wsgi_app(application)

if __name__ == "__main__":
	main()


