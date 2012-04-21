#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#MOPERで使う静止画像のキー値のHRDへの移行に対応するための、
#StringKey->ReferencePropertyのマッピング
#一時的なものです
#
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db

from MesThread import MesThread

class MoperKeyMapper(db.Model):
	str_thread_key = db.StringProperty()
	thread = db.ReferenceProperty(MesThread)

