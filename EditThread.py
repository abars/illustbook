#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

import re
import os

from Bbs import Bbs
from MesThread import MesThread
from OwnerCheck import OwnerCheck
from Alert import Alert
from CssDesign import CssDesign
from ReeditEscape import ReeditEscape

class EditThread(webapp.RequestHandler):
	def get(self):
		bbs=db.get(self.request.get("bbs_key"));
		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			self.response.out.write(Alert.alert_msg("編集する権限がありません。",self.request.host))
			return
		thread = db.get(self.request.get("thread_key"))
		
		summary=thread.summary
		postscript=""
		if(thread.postscript):
			postscript=thread.postscript
		
		summary=ReeditEscape.escape(summary);
		postscript=ReeditEscape.escape(postscript);
		
		host_url="./"
		design=CssDesign.get_design_object(self,bbs,host_url,1)
		
		template_values = {
			'bbs': bbs,
			'thread': thread,
			'summary': summary,
			'postscript': postscript,
			'template_path':design["template_path"],
			'css_name':design["css_name"],
			'is_iphone':design["is_iphone"],
			'template_base_color':design["template_base_color"],
		}

		path = os.path.join(os.path.dirname(__file__), 'mes_edit_thread.html')
		self.response.out.write(template.render(path, template_values))