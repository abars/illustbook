//-------------------------------------------------
//イラブペイント　チャットモード
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

var WATCH_DOG_COUNT=10;			//10回分の時間successが帰って来なかったらfailedと判断する
var GET_COMMAND_LIMIT=50;			//コマンドを読み込んでくる単位
var WORKER_INTERVAL=3000;			//3秒に一回通信

var CMD_DRAW=0;
var CMD_TEXT=1;
var CMD_HEART_BEAT=2;

//-------------------------------------------------
//グローバルコールバック
//-------------------------------------------------

var g_chat_key=null;	//チャットモードの場合はROOMのKEYが入る
var g_chat_user_id=null;	//ユーザのID
var g_chat_user_name="名無しさん";	//ユーザの名前

//チャットモードの場合は最初にinitが呼ばれる
function chat_init(key,user_id,user_name,server_time){
	//ユーザ情報
	g_chat_user_id=user_id
	g_chat_user_name=user_name
	
	//ローカルお絵かきモード
	if(key=="local" || key==""){
		return;
	}
	
	//チャットモード
	g_chat_key=key;
	
	//時間設定
	user_set_time_delta(server_time);
	
	//デバッグ用
	g_chat_user_name=g_chat_user_name;//+"_"+server_time
	g_chat_user_id=g_chat_user_id+"_"+server_time
}

//ワーカコールバック
function chat_worker(){
	g_chat._worker();
}

//コマンドGETコールバック
function chat_get_callback(obj){
	if(obj.status=="success"){
		g_chat._get_success(obj.command_list,obj.count);
	}
	if(obj.status=="failed"){
		g_chat._get_failed();
	}
}

//コマンドPOSTコールバック
function chat_post_callback(obj){
	if(obj.status=="success"){
		g_user.set_object_size(obj.size)
		g_chat._send_success();
	}
	if(obj.status=="failed"){
		g_chat._send_failed();
	}
}

//-------------------------------------------------
//チャットクラス
//-------------------------------------------------

function Chat(){
	this._geted_count;		//どのネットワークコマンドまでGETしているかの位置
	this._geting_count;		//今、GETしている数
	this._geting_retry;			//GETしてからの経過時間
	
	this._posted_count;		//どのローカルコマンドまでPOSTしているかの位置
	this._posting_count;		//今、POSTしている数
	this._posting_retry;		//POSTしてからの経過時間

	this._local_packet_count;		//ローカルのユニークパケットID

	
	//初期化
	this.init=function(){
		this._get_init();
		this._post_init();
		this._local_packet_count=0;
		setInterval(chat_worker,WORKER_INTERVAL);
	}
	
	//ワーカー
	this._worker=function(){
		//ローカルお絵かきモードの場合はPOSTしない
		if(g_chat_key==null)
			return;

		//最新のコマンドを取得する
		this._get();
		
		//コマンドを送信する
		this._send();
		
		//ハートビートを送信する
		g_user.send_heart_beat();
	}

//-------------------------------------------------
//GET系
//-------------------------------------------------

	this._get_init=function(){
		this._geted_count=0;
		this._geting_count=0;
		this._geting_retry=0;
	}
	
	//サーバから最新のコマンドリストを取得
	this._get=function(){
		//GET中はGETしない
		if(this._geting_count){
			this._geting_retry++;
			if(this._geting_retry>=WATCH_DOG_COUNT){
				this._get_failed();
			}
			return;
		}
		
		//コマンドリストを取得
		this._geting_retry=0;
		this._geting_count=GET_COMMAND_LIMIT
		illustbook.request.get("./chat?mode=get_command&offset="+this._geted_count+"&limit="+GET_COMMAND_LIMIT+"&key="+g_chat_key,chat_get_callback);
	}
	
	//コマンドの取得に成功した
	this._get_success=function(cmd_list,count){
		//コマンドを1つずつ処理
		for(var i=0;i<count;i++){
			var cmd=cmd_list[i];
			g_buffer.push_network_command(cmd);
		}
		
		//取得した位置を更新
		this._geted_count+=count;
		this._geting_count=0;
	}
	
	//コマンドの取得に失敗した
	this._get_failed=function(){
		this._geting_count=0;
	}

//-------------------------------------------------
//POST系
//-------------------------------------------------

	this._post_init=function(){
		this._posted_count=0;
		this._posting_count=0;
		this._posting_retry=0;
	}

	//サーバにコマンド送信
	this._send=function(){
		//送信するデータが存在するかを判定
		var len=g_buffer.get_local_command_len()-this._posted_count;
		if(len<=0){
			return;
		}
		
		//送信するデータを準備
		var cmd_list=new Array();
		for(var i=0;i<len;i++){
			var cmd=g_buffer.get_local_command(this._posted_count+i);
			cmd_list.push(cmd);
		}

		//送信中は送信しない
		if(this._posting_count){
			this._posting_retry=this._posting_retry+1;
			if(this._posting_retry>=WATCH_DOG_COUNT){
				this._send_failed();
			}
			return;
		}

		//送信
		this._posting_retry=0;
		this._send_core(cmd_list);
	}
	
	//サーバにコマンドリストを送信
	this._send_core=function(cmd_list){
		post_data=new Object();
		post_data["user_count"]=g_user.get_user_count();
		post_data["command_count"]=cmd_list.length;
		for(var i=0;i<cmd_list.length;i++){
			post_data["command"+i]=cmd_list[i];
		}
		this._posting_count=cmd_list.length;
		illustbook.request.post("./chat?mode=post_command&key="+g_chat_key,post_data,chat_post_callback);
	}
	
	this._send_success=function(){
		this._posted_count+=this._posting_count;
		this._posting_count=0;
	}
	
	this._send_failed=function(){
		this._posting_count=0;
	}

//-------------------------------------------------
//コマンドリスト構築
//-------------------------------------------------

	//チャットモードかどうか
	this.is_chat_mode=function(){
		return g_chat_key!=null
	}

	//ユーザID取得
	this.get_user_id=function(){
		return g_chat_user_id;
	}
	
	//パケットID取得
	this.get_packet_no=function(){
		this._local_packet_count++;
		return this._local_packet_count;
	}
	
	//ヘッダ作成
	this.create_command=function(cmd_no,obj){
		var txt="[{";
		txt+="'user_id':'"+g_chat.get_user_id()+"',"
		txt+="'packet_no':"+g_chat.get_packet_no()+","
		txt+="'cmd':"+cmd_no;
		for(tag in obj){
			var data=obj[tag];
			txt+=",";
			txt+="'"+tag+"':'"+data+"'";
		}
		txt+="}]";
		return txt;
	}

//-------------------------------------------------
//コメント
//-------------------------------------------------

	//コメントする
	this.comment=function(){
		var comment=document.getElementById("comment").value
		if(comment==""){
			return;
		}
		comment=""+g_chat_user_name+"＞"+comment;
		
		var obj=new Object();
		obj.comment=comment;
		var txt=this.create_command(CMD_TEXT,obj);
		
		g_buffer.push_command(txt);

		document.getElementById("comment").value=""
	}
}