//-------------------------------------------------
//イラブペイント　ハンド
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

function Hand(){
	this._hand_x=0;
	this._hand_y=0;

	this._before_x=0;
	this._begore_y=0;

	this._buttom_size;
	this._left_size;
	
	this._before_dist=0;

	this._flag=false;
	this._zoom=1;
	
	this.resize=function(offset_recalc){
		if(!offset_recalc){
			g_window_height=window.innerHeight;
		}
		
		var cheight=document.getElementById("canvas_event").clientHeight;

		var toolheight=0;//document.getElementById("toolbox").clientHeight;
		var new_height=(g_window_height-toolheight);
		document.getElementById("canvas_event").style.height=""+new_height+"px";
		
		if(offset_recalc){
			var add=(new_height-cheight)/2;
			this._hand_y+=add/this._zoom;
			can_div.style.top=this._hand_y;
		}
	}
	
	this.init=function(){
		this._buttom_size=200;
		if(g_chat_key==null){
			this._buttom_size=60;
		}
		this._left_size=60;
		
		this.resize(false);
		
		var margin=32;	//キャンバス外イベント確保用マージン
		
		var cwidth=document.getElementById("canvas_event").clientWidth-this._left_size;
		var cheight=document.getElementById("canvas_event").clientHeight-this._buttom_size;
	
		this._hand_x=Math.floor(cwidth-can_drawing[0].width)/2+this._left_size-margin;
		this._hand_y=Math.floor(cheight-can_drawing[0].height)/2-margin;

		can_div.style.left=""+this._hand_x+"px";
		can_div.style.top=""+this._hand_y+"px";
	}
	
	this.get_zoom=function(){
		return this._zoom;
	}
	
	this.get_prevent_draw=function(){
		return this._flag;
	}
	
	this.on_mouse_down=function(x,y,x2,y2){
		this._flag=true;
		this._before_x=0;
		this._before_dist=0;
	}
	
	this.on_mouse_up=function(x,y,x2,y2){
		this._flag=false;
	}
	
	this.on_mouse_move=function (x,y,x2,y2){
		if(!this._flag)
			return;

		var dist=Math.sqrt((x-x2)*(x-x2)+(y-y2)*(y-y2));

		if(this._before_x){
			this._hand_x+=x-this._before_x;
			this._hand_y+=y-this._before_y;
			can_div.style.top=""+Math.floor(this._hand_y)+"px";
			can_div.style.left=""+Math.floor(this._hand_x)+"px";
		}
		
		this._before_x=x;
		this._before_y=y;
	}
	
	this.zoom_in=function(){
		this._zoom_core(1.2);
	}
	
	this._zoom_core=function(m){
		var new_zoom=this._zoom*m;
		if(new_zoom<0.5){
			new_zoom=0.5;
		}

		this._hand_x-=(this._hand_x*new_zoom-this._hand_x*this._zoom)/new_zoom;
		this._hand_y-=(this._hand_y*new_zoom-this._hand_y*this._zoom)/new_zoom;
	
		this._hand_x-=(can_fixed[0].width*new_zoom-can_fixed[0].width*this._zoom)/2/new_zoom;
		this._hand_y-=(can_fixed[0].height*new_zoom-can_fixed[0].height*this._zoom)/2/new_zoom;
		
		can_div.style.left=""+Math.floor(this._hand_x)+"px";
		can_div.style.top=""+Math.floor(this._hand_y)+"px";

		this._zoom=new_zoom;
		can_div.style.zoom=""+Math.floor(this._zoom*100)+"%";
	}
	
	this.zoom_out=function(){
		this._zoom_core(1/1.2);
	}
	
	this.is_hand_mode=function(){
		return g_tool.get_tool()=="hand";
	}
}
