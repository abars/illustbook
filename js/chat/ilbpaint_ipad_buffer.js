//-------------------------------------------------
//イラブペイント　コマンドバッファ
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

function Buffer(){
	this._local_cmd_list;			//ローカルコマンド
	this._local_time_list;			//ローカルコマンドの時間
	this._network_cmd_list;	//ネットワークコマンド
	
	this._local_posted_cnt;		//ローカルコマンドの送信に成功した数
	this._reload_need;				//リロードが必要かどうか
	this._redo_buffer;				//REDOバッファ

	this.init=function(){
		this._local_cmd_list=new Array();
		this._local_time_list=new Array();
		this._network_cmd_list=new Array();
		this._local_posted_cnt=0;
		this._reload_need=false;
		this._redo_buffer=new Array();
	}

//-------------------------------------------------
//ローカルバッファにコマンドをPUSHする
//-------------------------------------------------
	
	this.push_command=function(command){
		//ローカルモードの場合は直接バッファに描いて確定してしまう
		if(!(g_chat.is_chat_mode())){
			this.push_network_command(command);
			for(var layer=0;layer<LAYER_N;layer++){
				g_draw_primitive.clear(can_local[layer]);
				can_local[layer].getContext("2d").drawImage(can_fixed[layer],0,0);
			}
			return;
		}
		
		//チャットモードの場合はローカルバッファに格納
		this._local_cmd_list.push(command);
		
		var cmd_kind=this._get_command_kind(command);

		if(cmd_kind==CMD_TEXT){
			this._local_time_list.push(0);	//チャットはすぐに反映
		}else{
			this._local_time_list.push(this.get_now_time());
		}
		
		if(cmd_kind==CMD_TEXT){
			var cmd_object=eval(command)[0];
			this._update_comment(cmd_object);	//今回のコメントを先行して反映してしまう
		}
		this._update_local_image();
	}
	
	this._update_local_image=function(){
		if(g_draw_canvas.is_drawing()){
			//線を書き終わったタイミングで自動的に更新が入る
			//ここで更新してしまうと消しゴムが動作しない
			return;
		}
		for(var layer=0;layer<LAYER_N;layer++){
			g_draw_primitive.clear(can_local[layer]);
			can_local[layer].getContext("2d").drawImage(can_fixed[layer],0,0);
		}
		this._command_exec(this._local_cmd_list,can_local,false);
	}
	
	this.undo_redo_exec_on_local_tool=function(){
		this._update_local_image();
	}
	
	this.get_local_command=function(send_pos){
		return this._local_cmd_list[send_pos-this._local_posted_cnt];
	}

	this.get_local_time=function(send_pos){
		return this._local_time_list[send_pos-this._local_posted_cnt];
	}
	
	this.get_local_command_len=function(){
		return this._local_cmd_list.length+this._local_posted_cnt;
	}
	
	this.pop_local_command=function(){
		this._local_cmd_list.shift();
		this._local_time_list.shift();
		this._local_posted_cnt++;
	}

//-------------------------------------------------
//ネットワークコマンドが到着
//-------------------------------------------------

	this.push_network_command=function(command){
		//ローカルコマンドと同じだった場合はローカルコマンドをpop
		if(command==this._local_cmd_list[0]){
			this.pop_local_command();
			this._update_local_image();
			var cmd=eval(command)[0].cmd;
			if(cmd==CMD_TEXT){	//自分の発言は既に処理されている
				return;
			}
		}
		
		//ネットワークコマンドを実行
		this._network_cmd_list.push(command);
		this._command_exec(this._network_cmd_list,can_fixed,true);
		this._network_cmd_list=new Array();
		this._update_local_image();
	}

//-------------------------------------------------
//コマンド実行
//-------------------------------------------------

	this._get_command_kind=function(cmd){
		var cmd_object=eval(cmd)[0];
		var cmd_kind=cmd_object["cmd"];
		return cmd_kind;
	}

	this._command_exec=function(cmd_list,dest_canvas,comment_exec){
		var context=new Array();
		for(var i=0;i<LAYER_N;i++){
			context[i]=dest_canvas[i].getContext("2d");
		}
		for(var i=0;i<cmd_list.length;i++){
			var cmd=cmd_list[i];
			var cmd_object=eval(cmd)[0];
			switch(cmd_object.cmd){
			case CMD_TEXT:
				if(comment_exec){
					this._update_comment(cmd_object);
				}
				break;
			case CMD_DRAW:
				g_draw_primitive.clear(can_work);
				g_draw_canvas.draw_command_list(can_work,cmd_list[i]);
				var alpha=cmd_object.alpha;
				var layer=cmd_object.layer;
				var color=cmd_object.color;
				var tool=cmd_object.tool;
				context[layer].globalAlpha=alpha
				if(tool=="eraser"){
					context[layer].globalCompositeOperation="destination-out";
				}
				context[layer].drawImage(can_work,0,0);
				context[layer].globalCompositeOperation="source-over";
				context[layer].globalAlpha=1.0;
				break;
			case CMD_HEART_BEAT:
				g_user.get_heart_beat(cmd_object);
				break;
			case CMD_NOP:
				if(!this._reload_need){
					alert("スナップショットの同期に失敗しました。リロードして復帰します。");
					window.location.reload();
					this._reload_need=true;
				}
				break;
			}
		}
	}
	
	this._update_comment=function(cmd_object){
		if(!(g_chat.is_chat_mode())){
			return;
		}
		document.getElementById("comment_list").value=cmd_object.comment+"\n"+document.getElementById("comment_list").value
	}

//-------------------------------------------------
//UNDO
//-------------------------------------------------

	this.undo=function(){
		var posted_count=g_chat.get_posted_count();
		if(this._local_cmd_list.length+this._local_posted_cnt<=posted_count){
			return;
		}
		var cmd=this._local_cmd_list[this._local_cmd_list.length-1]
		var kind=this._get_command_kind(cmd);
		if(kind==CMD_TEXT){	//チャットはUNDO禁止
			return;
		}
		this._redo_buffer.push(cmd);
		this._local_cmd_list.splice(this._local_cmd_list.length-1,1)
		this._local_time_list.splice(this._local_time_list.length-1,1)
		this._update_local_image();
	}

	this.redo=function(){
		if(this._redo_buffer.length<=0)
			return;
		var cmd=this._redo_buffer.shift();
		this.push_command(cmd);
	}
	
	this.redo_clear=function(){
		this._redo_buffer=new Array();
	}
	
	this.get_now_time=function(){
		var date = new Date();
		return date.getTime()
	}
};
