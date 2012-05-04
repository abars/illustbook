//-------------------------------------------------
//イラブペイント　コマンドバッファ
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

function Buffer(){
	this._local_cmd_list;			//ローカルコマンド
	this._network_cmd_list;	//ネットワークコマンド

	this._local_posted_cnt;		//ローカルコマンドの送信に成功した数

	this.init=function(){
		this._local_cmd_list=new Array();
		this._network_cmd_list=new Array();
		this._local_posted_cnt=0;
	}

//-------------------------------------------------
//ローカルバッファにコマンドをPUSHする
//-------------------------------------------------
	
	this.push_command=function(command){
		//ローカルモードの場合は直接バッファに描いて確定してしまう
		if(!(g_chat.is_chat_mode())){
			this.push_network_command(command);
			return;
		}
		
		//チャットモードの場合はローカルバッファに格納
		this._local_cmd_list.push(command);
		if(this._get_command_kind(command)==CMD_TEXT){
			var cmd_object=eval(command)[0];
			this._update_comment(cmd_object);	//今回のコメントを先行して反映してしまう
		}
		this._update_local_image();
	}
	
	this._update_local_image=function(){
		g_draw_primitive.clear(can_local);
		this._command_exec(this._local_cmd_list,can_local,false);
	}
	
	this.get_local_command=function(send_pos){
		return this._local_cmd_list[send_pos-this._local_posted_cnt];
	}
	
	this.get_local_command_len=function(){
		return this._local_cmd_list.length+this._local_posted_cnt;
	}
	
	this.pop_local_command=function(){
		this._local_cmd_list.shift();
		this._local_posted_cnt++;
	}

//-------------------------------------------------
//
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
		context=dest_canvas.getContext("2d");
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
				alpha=g_draw_canvas.draw_command_list(can_work,cmd_list[i]);
				context.globalAlpha=alpha
				context.drawImage(can_work,0,0);
				break;
			case CMD_HEART_BEAT:
				g_user.get_heart_beat(cmd_object);
				break;
			case CMD_NOP:
				break;
			case CMD_SNAPSHOT:
				var image=new Image();
				image.src="data:image/png;base64,"+cmd_object.snap_shot;
				image.onload=function(){
					g_draw_primitive.clear(can_fixed);
					can_fixed.getContext("2d").drawImage(image,0,0);
				}
				//本当はここでコマンドのパースを一時停止しなければならないが、
				//後で考えることにする
				break;
			}
		}
	}
	
	this._update_comment=function(cmd_object){
		document.getElementById("comment_list").value=cmd_object.comment+"\n"+document.getElementById("comment_list").value
	}
};
