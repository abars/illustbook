# illustbook
Illustration SNS for Google App Engine / py

![illustbook logo](https://github.com/abars/illustbook/blob/master/static_files/banner_360b.png)

# Demo

http://www.illustbook.net/

# Rquirement

GAE/py (StandardEnvironment)

Python2.7

Jinja2

# How to deploy

(1) Clone https://github.com/abars/illustbook

(2) Rewrite application ID of app.yaml (application: illust-book-hrd -> your id)

(3) Deploy to Google App Engine

If you require illustration tool for HTML5 , Please clone https://github.com/abars/illustbook_ipad and copy to js/ipad folder.

# Google Analytics Connection

Illustbook use Google Analytics for ranking calculation.

If your want to use ranking tab , You should rewrite SERVICE_ACCOUNT of app/AnalyticsGet.py and google_analytics_uacct of html/meta.html.

# Directory description

|folder|description|attribute|
|---|---|---|
|myapp|Application code||
|html|Html files for jinja2||
|js|Client side javascript|staticdir|
|static_files|Static files|staticdir|
|template|BBS design template|staticdir|
|tempform|BBS form design template|staticdir|
|flash|Illustration tool for FLASH|staticdir|
|js/ipad|Illustration tool for HTML5|staticdir|

# LICENSE

MIT license

# SUPPORT

https://twitter.com/abars

abarsceo@gmail.com
