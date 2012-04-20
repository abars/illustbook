#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#エラーが起きた時のエラー表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import re
import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache

from MappingId import MappingId

webapp.template.register_template_library('templatetags.django_filter')

class Alert(webapp.RequestHandler):
	@staticmethod
	def alert_msg(msg,host):
		host_url="http://"+MappingId.mapping_host(host)+"/";
		template_values = {
		'host': host_url,
		'alert_msg': msg
		}
		path = os.path.join(os.path.dirname(__file__), 'html/mes_alert.html')
		return template.render(path, template_values)
	
	@staticmethod
	def alert_msg_notfound(host):
		return Alert.alert_msg("掲示板が見つかりません。掲示板のURLが間違っているか、変更もしくは削除された可能性があります。urlがhttp://www.illustbook.net/usr/で始まっている掲示板は、AppEngineのHRDデータストアへの移行に伴い2011年11月1日からURLが変更になっています。<a href='http://"+host+"/mypage' class='declink'>マイページ</a>からログインして頂ければ、新しいURLを確認頂けます。また、デザインの設定から、変更されない固定のURLを割り当てることができますのでご利用頂ければと思います。ご迷惑をおかけします。",host)