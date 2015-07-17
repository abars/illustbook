# illustbook
Illustration SNS for Google App Engine / py

#概要

GoogleAppEngineで動くSNSシステムです。
http://www.illustbook.net/ で運用しています。
実装の参考にご利用下さい。

#動作環境

GAE/py

Python2.7(concurrent)

Jinja2

#フォルダ構成

myapp　サーバサイドのPythonコード

html　テンプレートエンジンに入力するhtmlファイル

js　クライアントサイドのJavaScript(staticdir)

static_files　各種静的ファイル(staticdir)

template　掲示板の標準デザインテンプレート(staticdir)

tempform 掲示板のフォームデザインテンプレート
