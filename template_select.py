#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#jinja2でレンダリング
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import os
import logging
import jinja2

import custom_filter

from myapp.SetUtf8 import SetUtf8

from google.appengine._internal.django.utils.html import strip_spaces_between_tags as short

def set_jinja_filter(jinja_environment):
	jinja_environment.filters.update({
			"time_JST":custom_filter.time_JST,
			"time_JST_format":custom_filter.time_JST_format,
			"time_JST_short":custom_filter.time_JST_short,
			"time_JST_progress":custom_filter.time_JST_progress,
			"time_UTC_progress":custom_filter.time_UTC_progress,
			"comment_with_except":custom_filter.comment_with_except,
			"comment_with_except_no_hour":custom_filter.comment_with_except_no_hour,
			"reply_with_except":custom_filter.reply_with_except,
			"image_key_with_except":custom_filter.image_key_with_except,
			"div":custom_filter.div,
			"admin_comment_with_except":custom_filter.admin_comment_with_except,
			"show_bookmark":custom_filter.show_bookmark,
			"show_bookmark_bbs":custom_filter.show_bookmark_bbs,
			"add_bookmark_bbs":custom_filter.add_bookmark_bbs,
			"add_bookmark_thread":custom_filter.add_bookmark_thread,
			"show_app":custom_filter.show_app,
			"show_app_iphone":custom_filter.show_app_iphone,
			"show_app_mypage":custom_filter.show_app_mypage,
			"author_name_thread":custom_filter.author_name_thread,
			"author_name_comment":custom_filter.author_name_comment,
			"user_id_to_user_name":custom_filter.user_id_to_user_name,
			"separate_nico":custom_filter.separate_nico,
			"login_url":custom_filter.login_url,
			"logout_url":custom_filter.logout_url,
			"new_feed_count":custom_filter.new_feed_count,
			"set_seed":custom_filter.set_seed,
			"auto_link":custom_filter.auto_link,
			"thumbnail2_width":custom_filter.thumbnail2_width,
			"thumbnail2_height":custom_filter.thumbnail2_height,
			'iriencode': custom_filter.iriencode,
			'regulation_check': custom_filter.regulation_check,
			'regulation_name': custom_filter.regulation_name,
			'ip_hash': custom_filter.ip_hash,
			'truncate_category': custom_filter.truncate_category,
			'truncate_tweet': custom_filter.truncate_tweet,
			'host_for_js': custom_filter.host_for_js,
			"escape_single_quotation": custom_filter.escape_single_quotation
	})

jinja_environment_html = jinja2.Environment(loader=jinja2.FileSystemLoader("html/"))
jinja_environment_temp = jinja2.Environment(loader=jinja2.FileSystemLoader("tempform/"))

set_jinja_filter(jinja_environment_html)

def render(template_path, template_dict, debug=False):
	SetUtf8.set()
	path_list=template_path.split("/")
	new_path=""
	for i in range(2,len(path_list)):
		new_path+="/"+path_list[i]

	if(path_list[1]=="tempform"):
		jinja_template = jinja_environment_temp.get_template(new_path)	
	else:
		jinja_template = jinja_environment_html.get_template(new_path)	
	render_value=jinja_template.render(template_dict)
	#return render_value
	return short(render_value)
