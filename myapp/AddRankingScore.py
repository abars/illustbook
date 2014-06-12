#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#削除予定
#---------------------------------------------------

import datetime;
import time;
import json;
import logging;

from google.appengine.ext import db
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp

class AddRankingScore(webapp.RequestHandler):
	def post(self):
		return

	@staticmethod
	def add_rank_direct(thread_key,user_id,score):
		return

