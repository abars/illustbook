# illustbook
Illustration SNS for Google App Engine / py

![illustbook logo](https://github.com/abars/illustbook/blob/master/static_files/banner_360b.png)

# 概要

GoogleAppEngineで動くSNSシステムです。

http://www.illustbook.net/ で運用しています。

# 動作環境

GAE/py

Python2.7

Jinja2

# デプロイ方法

(1) https://github.com/abars/illustbook をCloneします

(2) app.yamlのapplication: illust-book-hrdを書き換えます

(3) GoogleAppEngineのStandardEnvironmentにdeployします

iPad版のお絵かきツールが必要な場合は、 https://github.com/abars/illustbook_ipad をCloneしてjs/ipadフォルダに配置して下さい。

PullRequestも受け付けています。

# フォルダ構成

myapp　サーバサイドのPythonコード

html　テンプレートエンジンに入力するhtmlファイル

js　クライアントサイドのJavaScript(staticdir)

static_files　各種静的ファイル(staticdir)

template　掲示板の標準デザインテンプレート(staticdir)

tempform 掲示板のフォームデザインテンプレート

flash お絵かきツールのバイナリ(staticdir)

js/ipad お絵かきツール(HTML5版)(staticdir)

