from google.appengine.ext import db

class NewsRss(db.Model):
    url=db.StringProperty()