#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#エラーが起きた時のエラー表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import re
import os

import template_select

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import memcache

from myapp.MappingId import MappingId
from myapp.CssDesign import CssDesign

class Alert(webapp.RequestHandler):
	@staticmethod
	def alert_msg(msg,host):
		is_iphone=0
		is_english=0
		return Alert.alert_msg_core(msg,host,is_iphone,is_english)

	@staticmethod
	def alert_msg_with_write(req,msg):
		is_iphone=CssDesign.is_iphone(req)
		host=req.request.host
		is_english=CssDesign.is_english(req)
		req.response.out.write(Alert.alert_msg_core(msg,host,is_iphone,is_english))

	@staticmethod
	def alert_spam(req,content,msg):
		content="<br/><br/><textarea style='width:100%' rows=10>"+content+"</textarea>"
		Alert.alert_msg_with_write(req,msg+content)

	@staticmethod
	def alert_msg_core(msg,host,is_iphone,is_english):
		host_url="http://"+MappingId.mapping_host(host)+"/";
		user=users.get_current_user()
		template_values = {
		'host': host_url,
		'alert_msg': msg,
		'is_iphone': is_iphone,
		'is_english': is_english,
		'user':user,
		'redirect_url': host_url
		}
		path = '/html/alert.html'
		return template_select.render(path, template_values)
	
	@staticmethod
	def alert_msg_notfound(req):
		is_english=CssDesign.is_english(req)
		if(is_english):
			msg="Bbs not found"
		else:
			msg="掲示板が見つかりません。掲示板のURLが間違っているか、変更もしくは削除された可能性があります。"
			msg+="urlがhttp://www.illustbook.net/usr/で始まっている掲示板は、AppEngineのHRDデータストアへの移行に伴い2011年11月1日からURLが変更になっています。"
			msg+="マイページからログインして頂ければ、新しいURLを確認頂けます。"
			msg+="また、デザインの設定から、変更されない固定のURLを割り当てることができますのでご利用頂ければと思います。ご迷惑をおかけします。"
		Alert.alert_msg_with_write(req,msg)

