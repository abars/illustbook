//-------------------------------------------------
//イラブペイント　ログインユーザ管理
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

var HEART_BEAT_SEC=60;

var g_server_time_delta=0;

function user_set_time_delta(server_time){
	var date = new Date();
	g_server_time_delta=server_time-date.getTime()/1000;
}

function User(){
	this._user_list;
	this._before_send_heart_beat_time;
	this._datastore_size;
	
	this.init=function(){
		this._user_list=new Array();
		this._before_send_heart_beat_time=0;
		this._datastore_size=0;
	}
	
	//ユーザ一覧を表示
	this._show_all_user=function(){
		var txt="";
		for(var i=0;i<this._user_list.length;i++){
			var user=this._user_list[i];
			var name=user.name;
			var id=user.id.split("_")[0];
			txt+="<a href='./mypage?user_id="+id+"' target='_BLANK'>";
			txt+="<img src='./show_icon?key="+id+"' width=30px height=30px>";
			txt+="</a>";
		}
		txt+="<BR><small>"+this._user_list.length+"人参加</small>";

		document.getElementById("user_list").innerHTML=txt;
	}
	
	this._update_status=function(){
		var perc=this._datastore_size;
		var txt="<small>容量の"+perc+"%を使用</small>";
		document.getElementById("status").innerHTML=txt;
	}
	
	//ログアウトチェック
	this._logout=function(){
		for(var i=0;i<this._user_list.length;i++){
			var user=this._user_list[i];
			var sec=((this._get_now_time()-user.time));
			if(sec>=HEART_BEAT_SEC){
				g_buffer._update_comment({"comment":""+user.name+"さんが退室しました。"});
				this._user_list.splice(i,1);
				this._show_all_user();	//ステータス更新
				return;
			}
		}
	}
	
	//ハートビートを受け取る
	this.get_heart_beat=function(cmd_object){
		var name=cmd_object.user_name;
		var id=cmd_object.user_id;
		var time=cmd_object.time;

		this._logout();

		for(var i=0;i<this._user_list.length;i++){
			if(this._user_list[i].id==id){
				this._user_list[i].time=time;
				return;
			}
		}
		
		//古すぎるものは受理しない
		var sec=this._get_now_time()-time;
		if(sec>=HEART_BEAT_SEC){
			return;
		}
		
		//ユーザ追加
		this._add_user(name,id,time);
	}
	
	//ユーザ追加
	this._add_user=function(name,id,time){
		g_buffer._update_comment({"comment":""+name+"さんが参加しました。"});

		var obj=new Object();
		obj.name=name;
		obj.id=id;
		obj.time=time;
		this._user_list.push(obj);

		this._show_all_user();
	}
	
	//ハートビートを送信する
	this.send_heart_beat=function(){
		//一定時間間隔で送信
		var now_time=this._get_now_time();
		var progress=now_time-this._before_send_heart_beat_time;
		if(progress<HEART_BEAT_SEC/10){
			return;
		}
		this._before_send_heart_beat_time=now_time;
		
		//送信
		var obj=new Object();
		obj.user_name=g_chat_user_name;
		obj.user_id=g_chat_user_id;
		obj.time=this._get_now_time();
		var txt=g_chat.create_command(CMD_HEART_BEAT,obj);
		g_buffer.push_command(txt);
	}
	
	this._get_now_time=function(){
		var date = new Date();
		return date.getTime()/1000+g_server_time_delta;
	}
	
	this.get_user_count=function(){
		return this._user_list.length;
	}
	
	this.set_object_size=function(size){
		this._datastore_size=Math.round((size*100)/(1*1024*1024));
		this._update_status();
		return this._datastore_size
	}
}
