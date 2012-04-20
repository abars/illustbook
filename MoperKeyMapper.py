#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#MOPERで使う静止画像のキー値のHRDへの移行に対応するための、
#StringKey->ReferencePropertyのマッピング

from google.appengine.ext import db

from MesThread import MesThread

class MoperKeyMapper(db.Model):
	str_thread_key = db.StringProperty()
	thread = db.ReferenceProperty(MesThread)

