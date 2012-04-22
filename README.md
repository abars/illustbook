お絵かき掲示板システム of illustbook.net
=============

概要
-------

GoogleAppEngineで動く掲示板システムです。
MITライセンスです。
実際に
http://www.illustbook.net/
で運用しています。

動作環境
-------

GoogleAppEngine1.6.4

Python2.7(concurrent)

Django1.2

フォルダ構成
-------

html　テンプレートエンジンに入力するhtmlファイル

js　クライアントサイドのJavaScript(staticdir)

myapp　サーバサイドのPythonコード

static_files　各種静的ファイル(staticdir)

template　掲示板の標準デザインテンプレート(staticdir)

template_custom　掲示板のユーザカスタムデザインテンプレート

templatetags　djangoのカスタムフィルタ

動作方法
-------

まだhtmlをpushしていないため動作させることはできません。
実装の参考程度にどうぞ。

ステータス
-------

コード整理中。
