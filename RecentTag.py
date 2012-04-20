from google.appengine.ext import db
from google.appengine.api import users

class RecentTag(db.Model):
	tag_list = db.StringListProperty()
	score_list = db.StringListProperty()