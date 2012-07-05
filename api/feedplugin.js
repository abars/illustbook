//プラグイン概要
//掲示板に投稿された新着投稿のサムネイルを表示します。
//引数のbbs_idで掲示板、illust_nで表示イラスト数、illust_sizeで表示サイズを変更することで、
//表示数を変更することができます。

//プラグインデフォルト引数
//bbs_id=sample&illust_n=8&illust_size=50

//プラグインメインクラス
function NewsPlugin(){
	this._div=null; //プラグイン領域への参照
    this._size=100; //表示する画像サイズ
}

//illustbook.app.regist直後に呼ばれる
NewsPlugin.prototype.init=function(){
    //divを取得する
    this._div=illustbook.app.getDiv(this);

    //プラグイン引数を取得する
    var args=illustbook.utility.getUrlArg();
    this._size=illustbook.utility.getUrlArg().illust_size;
    
    //JSONPでfeedAPIを呼び出し
    illustbook.feed.getThreadList(args.bbs_id,0,args.illust_n,illustbook.feed.ORDER_NONE,illust_callback);
};

//JSON APIコールバック
NewsPlugin.prototype.illust_callback=function(oj){
    //API呼び出しに失敗した場合はエラーメッセージを返す
    if(oj.status!="success"){
        this._div.innerHTML=oj.message;
        return;
    }
    
    //イラストのリストを作成
    var news_html="";
    for(var i=0;i<oj.response.length;i++){
        var thread=oj.response[i];
        news_html+="<a href='"+thread.thread_url+"' target='_blank'>";
        news_html+="<img src='"+thread.thumbnail_url+"' width="+this._size+" height="+this._size+" border=0>";
        news_html+="</a>";
    }    
    this._div.innerHTML=news_html;
};

//コールバック呼び出し
function illust_callback(oj){
    news_plugin.illust_callback(oj);
}

//イラストブックにプラグインを登録する
var news_plugin=new NewsPlugin();
illustbook.app.regist(news_plugin);
