#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#エラーが起きた時のエラー表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import re
import os

import template_select

from google.appengine.ext import webapp
from google.appengine.api import memcache

from myapp.MappingId import MappingId
from myapp.CssDesign import CssDesign

class Alert(webapp.RequestHandler):
	@staticmethod
	def alert_msg(msg,host):
		is_iphone=0
		return Alert.alert_msg_core(msg,host,is_iphone)

	@staticmethod
	def alert_msg_with_write(req,msg):
		is_iphone=CssDesign.is_iphone(req)
		host=req.request.host
		req.response.out.write(Alert.alert_msg_core(msg,host,is_iphone))

	@staticmethod
	def alert_msg_core(msg,host,is_iphone):
		host_url="http://"+MappingId.mapping_host(host)+"/";
		template_values = {
		'host': host_url,
		'alert_msg': msg,
		'is_iphone': is_iphone
		}
		path = '/html/alert.html'
		return template_select.render(path, template_values)
	
	@staticmethod
	def alert_msg_notfound(req):
		msg="掲示板が見つかりません。掲示板のURLが間違っているか、変更もしくは削除された可能性があります。"
		msg+="urlがhttp://www.illustbook.net/usr/で始まっている掲示板は、AppEngineのHRDデータストアへの移行に伴い2011年11月1日からURLが変更になっています。"
		msg+="マイページからログインして頂ければ、新しいURLを確認頂けます。"
		msg+="また、デザインの設定から、変更されない固定のURLを割り当てることができますのでご利用頂ければと思います。ご迷惑をおかけします。"
		Alert.alert_msg_with_write(req,msg)

