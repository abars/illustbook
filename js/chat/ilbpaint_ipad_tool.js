//-------------------------------------------------
//イラブペイント　基本ツール
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

//-------------------------------------------------
//アルファ
//-------------------------------------------------

function Alpha(){
	this._alpha=1.0;

	this.init=function(){
	}

	this.get_alpha=function(){
		return this._alpha;
	}
	
	this.update=function(){
	}
	
	this.on_change=function(){
		this._alpha=Number(document.getElementById("slider_alpha").value)/100.0;
	}
}

//-------------------------------------------------
//パレット
//-------------------------------------------------

function Palette(){
	//メンバ変数
	this._color="rgba(255,0,0,1)";
	this._palette_color=new Array();
	this._palette_color_n;

	//クリックした
	this.on_click=function(color,is_touch){
		var new_color=this._palette_color[color];
		
		this._color=new_color;
		
		g_alpha.update();
		
		for(var i=0;i<this._palette_color_n;i++){
			var w=g_color_width;
			var h=g_color_width;
			var alpha=1;
			if(i==color){
				w=g_color_width-8;
				h=g_color_width-8;
				document.getElementById("palette"+i).style.border="solid 4px #ffffff";
			}else{
				document.getElementById("palette"+i).style.border="none";
			}
			document.getElementById("palette"+i).style.width=w;
			document.getElementById("palette"+i).style.height=h;
		}
	}

	this.init=function(){
		this._palette_color[0]="#000000";
		this._palette_color[1]="#404040";
		this._palette_color[2]="#606060";
		this._palette_color[3]="#808080";
		this._palette_color[4]="#a0a0a0";
		this._palette_color[5]="#c0c0c0";
		this._palette_color[6]="#eeeeee";
		this._palette_color[7]="#ffffff";
		this._palette_color[8]="#bc700c";
		this._palette_color[9]="#ec9d86";
		this._palette_color[10]="#ffc39e";
		this._palette_color[11]="#ffd9c2";
		this._palette_color[12]="#ff0000";
		this._palette_color[13]="#ffacac";
		this._palette_color[14]="#d894e0";
		this._palette_color[15]="#0000ff";
		this._palette_color[16]="#00ffff";
		this._palette_color[17]="#50ff50";
		this._palette_color[18]="#50bc50";
		this._palette_color[19]="#ffff00";
		
		this._palette_color_n=20;
		var txt="";
		for(var i=0;i<this._palette_color_n;i++){
			txt+="<div id='palette"+i+"'style='float:left;width:"+g_color_width+"px;height:"+g_color_width+"px;background-color:"+this._palette_color[i]+";'";
			if(ipad_is_pc()){
				txt+=" onclick='javascript:g_palette.on_click("+i+",false);'";
			}
			txt+=">";
			txt+="</div>";
		}
		document.getElementById("palette").innerHTML=txt;

		if(!ipad_is_pc()){
		    for(var i=0;i<this._palette_color_n;i++){
				document.getElementById("palette"+i).addEventListener("touchstart", function(){g_palette.on_click(this.id.split("palette")[1],true);},false);
		    }
		}
		
		this.on_click(0);
	}
	
	this.get_color=function(){
		if(g_tool.get_tool()=="eraser"){
			return "#ffffff";
		}
		return this._color;
	}
}

//-------------------------------------------------
//ツールボックス
//-------------------------------------------------

function ToolBox(){
	this._add_button=function(cmd,info,s,margin){
		var button_style="margin:2px;margin-left:4px;text-align:center;width:"+g_button_width+"px;height:"+g_button_height+"px;border:solid 1px #5f5fef;background-color:#c7e5f9;";
		var txt='<div id="'+cmd+'"';
		if(ipad_is_pc()){
			txt+=' onclick="javascript:'+cmd+'(false);"';
		}
		txt+=' style="'+button_style+'margin-top:'+margin+'px;">'+info+'</div>';
		return txt;
	}
	
	this.init=function(){
		var txt="";
		var s=g_button_width+20;
		var margin=12;
		txt+=this._add_button("g_undo_redo.undo","取り消し",s,margin);
		txt+=this._add_button("g_undo_redo.redo","やり直し",s,0);

		txt+=this._add_button("g_tool.set_pen","ペン",s,margin);
		txt+=this._add_button("g_tool.set_eraser","消しゴム",s,0);
		txt+=this._add_button("g_tool.set_hand","ハンド",s,0);

		txt+=this._add_button("g_hand.zoom_in","ズーム<BR>+",s,margin);
		txt+=this._add_button("g_hand.zoom_out","ズーム<BR>-",s,0);
		if(!(g_chat.is_chat_mode())){
			txt+=this._add_button("g_draw_canvas.clear","クリア",s,margin);
		}
		if(!(g_chat.is_view_mode())){
			txt+=this._add_button("ipad_switch_upload_form","投稿",s,margin);
		}
		
		//デバッグ
		if(SNAPSHOT_ALERT){
			txt+=this._add_button("g_chat.prepare_snapshot();g_chat.snapshot();","スナップ",s,margin);
		}

		document.getElementById("toolmenu").innerHTML=txt+"<br clear='both'>";

		//遅延登録が必須
		if(!ipad_is_pc()){
			document.getElementById("g_undo_redo.undo").addEventListener("touchstart", function(e){g_undo_redo.undo(true);},false);
			document.getElementById("g_undo_redo.redo").addEventListener("touchstart", function(e){g_undo_redo.redo(true);},false);
			document.getElementById("g_tool.set_pen").addEventListener("touchstart", function(e){g_tool.set_pen();},false);
			document.getElementById("g_tool.set_eraser").addEventListener("touchstart", function(e){g_tool.set_eraser();},false);
			document.getElementById("g_tool.set_hand").addEventListener("touchstart", function(e){g_tool.set_hand();},false);
			document.getElementById("g_hand.zoom_out").addEventListener("touchstart", function(e){g_hand.zoom_out(true);},false);
			document.getElementById("g_hand.zoom_in").addEventListener("touchstart", function(e){g_hand.zoom_in(true);},false);
			if(!(g_chat.is_chat_mode())){
				document.getElementById("g_draw_canvas.clear").addEventListener("touchstart", function(e){g_draw_canvas.clear(true);},false);
			}
			if(!(g_chat.is_view_mode())){
				document.getElementById("ipad_switch_upload_form").addEventListener("touchstart", function(e){ipad_switch_upload_form(true);},false);
			}
		}
	}

	this.update=function(){
		var color="#c7e5f9";
		if(g_hand.is_hand_mode()){
			color="#a7c5d9"
		}
		document.getElementById("g_hand.hand_mode").style["background-color"]=color;
	}
}

//-------------------------------------------------
//ペンサイズ
//-------------------------------------------------

function PenSize(){
	this._size=1;
	this._n=9;

	this.init=function(){
		var txt="";
		this._size=4;
	}
	
	this.on_change=function(){
		this._size=document.getElementById("slider_size").value;
	}

	this.get_size=function (){
		return this._size;
	}
}

//-------------------------------------------------
//ツール
//-------------------------------------------------

function Tool(){
	this._tool;
	
	this.init=function(){
		this._set_core("pen");
	}
	
	this.set_hand=function(){
		this._set_core("hand");
	}
	
	this.set_pen=function(){
		this._set_core("pen");
	}
	
	this.set_eraser=function(){
		this._set_core("eraser");
	}
	
	this._set_core=function(tool){
		var color="#c7e5f9";
		document.getElementById("g_tool.set_pen").style["background-color"]=color;
		document.getElementById("g_tool.set_eraser").style["background-color"]=color;
		document.getElementById("g_tool.set_hand").style["background-color"]=color;

		color="#a7c5d9"
		document.getElementById("g_tool.set_"+tool).style["background-color"]=color;
		
		this._tool=tool;
	}
	
	this.get_tool=function(){
		return this._tool;
	}
}

