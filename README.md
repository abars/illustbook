お絵かき掲示板システム of illustbook.net
=============

概要
-------

GoogleAppEngineで動く掲示板システムです。
公開しているソースコードはMITライセンスです。

実際に
http://www.illustbook.net/
で運用しています。

お絵かきツールを公開する予定はないため、動作させることはできません。
実装の参考にご利用下さい。

動作環境
-------

GoogleAppEngine1.7

Python2.7(concurrent)

Jinja2

フォルダ構成
-------

myapp　サーバサイドのPythonコード

html　テンプレートエンジンに入力するhtmlファイル

js　クライアントサイドのJavaScript(staticdir)

static_files　各種静的ファイル(staticdir)

template　掲示板の標準デザインテンプレート(staticdir)

tempform 掲示板のフォームデザインテンプレート
