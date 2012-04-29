#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板の設定に応じてCSSを取得する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os
import re

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8

webapp.template.register_template_library('templatetags.django_filter')

class CssDesign (webapp.RequestHandler):
	@staticmethod
	def get_bbs_base_name(css):
		return "bbs.html"

	@staticmethod
	def get_thread_base_name(css):
		return "thread.html"

	@staticmethod
	def get_template_path(host_url,css):
		if(not css):
			return ""
		if(css == 0):
			return "";
		if(css == 1):
			return host_url+"template/blue/"
		if(css == 2):
			return host_url+"template/green/"
		if(css == 3):
			return host_url+"template/pink/"
		if(css == 4):
			return host_url+"template/white/"
		return ""

	@staticmethod
	def get_base_color(css):
		if(not css):
			return ""
		if(css ==0):
			return ""
		if(css == 1):
			return "9ECBEB"
		if(css == 2):
			return "A8D2AD"
		if(css == 3):
			return "FFB9CF"
		if(css == 4):
			return "536566"
		return ""
	
	@staticmethod
	def is_iphone(main):
		#return 1
		agent=str(main.request.headers['User-Agent'])
		p = re.compile('iPhone')
		if(p.search(agent)):
			return 1
		p = re.compile("Android.*Mobile");
		if(p.search(agent)):
			return 1
		if(main.request.get("is_iphone")):
			if(main.request.get("is_iphone")=="1"):
				return 1
		return 0

	@staticmethod
	def is_tablet(main):
		agent=str(main.request.headers['User-Agent'])

		p = re.compile('iPad')
		if(p.search(agent)):
			return 1

		#p = re.compile("Android.*Mobile");
		#if(p.search(agent)):
		#	return 0

		#p = re.compile("Android");
		#if(p.search(agent)):
		#	return 1

		return 0
	
	@staticmethod
	def get_css_name(host_url,css,is_thread,is_iphone,in_frame_mode):
		if(is_iphone):
			return CssDesign.get_template_path(host_url,css)+"style_iphone.css";
		if(is_thread or in_frame_mode):
			return CssDesign.get_template_path(host_url,css)+"style_1col.css";
		return CssDesign.get_template_path(host_url,css)+"style_2col.css";

	@staticmethod
	def get_design_object(main,bbs,host_url,is_thread):
		is_iphone=CssDesign.is_iphone(main)
		is_tablet=CssDesign.is_tablet(main)
		
		design_template_no=bbs.design_template_no
		if(main.request.get("css")):
			design_template_no=int(main.request.get("css"))
		if(main.request.get("css_key")):
			design_template_no=0
		if(is_thread):
			base_name=CssDesign.get_thread_base_name(design_template_no)
		else:
			base_name=CssDesign.get_bbs_base_name(design_template_no)
		template_path=CssDesign.get_template_path(host_url,design_template_no)
		template_base_color=CssDesign.get_base_color(design_template_no)
		css_name=CssDesign.get_css_name(host_url,design_template_no,is_thread,is_iphone,bbs.in_frame_mode)

		dict={}
		dict["is_iphone"]=is_iphone
		dict["is_tablet"]=is_tablet
		dict["template_path"]=template_path
		dict["css_name"]=css_name
		dict["template_base_color"]=template_base_color
		dict["base_name"]=base_name

		return dict

	def get(self,bbs_or_css_key,mode):
		bbs=None
		user_css=None

		if(mode=="css"):
			#bbs apply
			try:
				bbs = db.get(bbs_or_css_key)
			except:
				bbs=None
			if(bbs and bbs.design_template_no and bbs.design_template_no==32767):
				if(bbs.css):
					user_css=bbs.css
		else:
			#test apply
			try:
				user_css = db.get(bbs_or_css_key)
			except:
				user_css=None

		if(bbs==None and user_css==None):
			self.error(404)
			return
		
		is_iphone=CssDesign.is_iphone(self)
		
		template_values = {
			'bbs':bbs,
			'user_css': user_css,
			'is_iphone':is_iphone
		}

		path = os.path.join(os.path.dirname(__file__), '../template_custom/style_main.htm')
		res=template.render(path, template_values)
		
		self.response.headers['Content-Type']= 'text/css'
		self.response.out.write(res)