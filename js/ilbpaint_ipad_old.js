//-------------------------------------------------
//イラブペイント　iPad版
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

var HAND_DEBUG=false;

//-------------------------------------------------
//スクリプト読込
//-------------------------------------------------

//function addJS(file){
//	document.write('<script type="text/javascript" src="'+file+'"></script>');
//}

//addJS("js/ilbpaint_ipad_color.js");
//addJS("js/ilbpaint_ipad_layer.js");

//-------------------------------------------------
//インスタンス化
//-------------------------------------------------

var g_draw_canvas=new DrawCanvas();
var g_palette=new Palette();
var g_pen_size=new PenSize();
var g_upload=new Upload();
var g_undo_redo=new UndoRedo();
var g_hand=new Hand();
var g_alpha=new Alpha();
var g_tool_box=new ToolBox();

function ipad_init(){
	ipad_get_instance();
	ipad_event_init();
	
	g_tool_box.init();
	g_palette.init();
	g_alpha.init();
	g_pen_size.init();
	g_hand.init();
}

//-------------------------------------------------
//インスタンス取得
//-------------------------------------------------

var can_back;
var can_drawing;
var can_div;

var g_button_width;
var g_color_width;
var g_window_height;

function ipad_get_instance(){
	can_div = document.getElementById("canvas_div"); 
	can_back = document.getElementById("canvas_back"); 
	can_drawing = document.getElementById("canvas_drawing");
	
	g_button_width=document.getElementById("canvas_event").clientWidth/16;
	g_color_width=document.getElementById("canvas_event").clientWidth/10-1;
}

//-------------------------------------------------
//イベント
//-------------------------------------------------

function ipad_event_init(){
	can_div.addEventListener("mousemove", ipad_on_mouse_move, false);
	can_div.addEventListener("mousedown", ipad_on_mouse_down , false);
	can_div.addEventListener("mouseup", ipad_on_mouse_up,false);

	can_div.addEventListener("touchmove", ipad_on_mouse_move, false);
	can_div.addEventListener("touchstart", ipad_on_mouse_down , false);
	can_div.addEventListener("touchend", ipad_on_mouse_up,false);
	
	can_div.addEventListener("gesturestart", function(e){ e.preventDefault();},false);

	var can_event=document.getElementById("canvas_event");
	can_event.addEventListener("touchstart", function(e){ e.preventDefault();},false);
}

function ipad_on_mouse_move(e){
	if(e.touches){
		e.preventDefault();
		if(e.touches.length>=2){
			g_hand.on_mouse_move(e.touches[0].clientX,e.touches[0].clientY,e.touches[1].clientX,e.touches[1].clientY);
			return;
		}
		if(!g_hand.get_prevent_draw()){
			g_draw_canvas.on_mouse_move(e.touches[0].clientX,e.touches[0].clientY);
		}
		return;
	}
	if(HAND_DEBUG){
		g_hand.on_mouse_move(e.clientX,e.clientY,0,0);
		return;
	}
	g_draw_canvas.on_mouse_move(e.clientX,e.clientY);
}

function ipad_on_mouse_down(e){
	if(e.touches){
		e.preventDefault();
		if(e.touches.length>=2){
			g_hand.on_mouse_down(e.touches[0].clientX,e.touches[0].clientY,e.touches[1].clientX,e.touches[1].clientY);
			return;
		}
		g_draw_canvas.on_mouse_down(e.touches[0].clientX,e.touches[0].clientY);
		return;
	}
	if(HAND_DEBUG){
		g_hand.on_mouse_down(e.clientX,e.clientY,0,0);
		return;
	}
	g_draw_canvas.on_mouse_down(e.clientX,e.clientY);
}

function ipad_on_mouse_up(e){
	e.preventDefault();
	if(g_hand.get_prevent_draw()){
		g_draw_canvas.release_flag();
	}
	g_draw_canvas.on_mouse_up(0,0);
	g_hand.on_mouse_up(0,0,0,0);
}

function ipad_is_pc(){
	return (window.ontouchstart===undefined);
}

//-------------------------------------------------
//アップロード通知
//-------------------------------------------------

function ipad_upload_callback(oj){
	if(oj.responseText.match("success")){
		g_upload.go_bbs();
		return;
	}
	alert("アップロードに失敗しました。");
	//alert(oj.responseText);
}

//-------------------------------------------------
//ツールクリック
//-------------------------------------------------

function ipad_switch_upload_form(is_touch){
	ipad_switch_form(is_touch,"upload_form");
}

function ipad_switch_palette_form(is_touch){
	ipad_switch_form(is_touch,"palette_form");
}

function ipad_switch_pen_form(is_touch){
	ipad_switch_form(is_touch,"pensize_form");
}

function ipad_switch_form(is_touch,mode){
	if(document.getElementById(mode).style.display=="block"){
		document.getElementById(mode).style.display='none';
	}else{
		document.getElementById(mode).style.display='block';
	}
	g_hand.resize(true);
}

//-------------------------------------------------
//ハンドクラス
//-------------------------------------------------

function Hand(){
	this._hand_x=0;
	this._hand_y=0;

	this._before_x=0;
	this._begore_y=0;
	
	this._before_dist=0;

	this._flag=false;
	this._zoom=1;
	
	this.resize=function(offset_recalc){
		if(!offset_recalc){
			g_window_height=window.innerHeight;
		}
		
		var cheight=document.getElementById("canvas_event").clientHeight;

		var toolheight=document.getElementById("toolbox").clientHeight;
		var new_height=(g_window_height-toolheight);
		document.getElementById("canvas_event").style.height=""+new_height+"px";
		
		if(offset_recalc){
			var add=(new_height-cheight)/2;
			this._hand_y+=add/this._zoom;
			can_div.style.top=this._hand_y;
		}
	}
	
	this.init=function(){
		this.resize(false);
	
		var cwidth=document.getElementById("canvas_event").clientWidth;
		var cheight=document.getElementById("canvas_event").clientHeight;
	
		this._hand_x=Math.floor(cwidth-can_drawing.width)/2;
		this._hand_y=Math.floor(cheight-can_drawing.height)/2;

		can_div.style.left=this._hand_x;
		can_div.style.top=this._hand_y;
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
			can_div.style.top=this._hand_y;
			can_div.style.left=this._hand_x;
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
	
		this._hand_x-=(can_back.width*new_zoom-can_back.width*this._zoom)/2/new_zoom;
		this._hand_y-=(can_back.height*new_zoom-can_back.height*this._zoom)/2/new_zoom;
		
		can_div.style.left=this._hand_x;
		can_div.style.top=this._hand_y;

		this._zoom=new_zoom;
		can_div.style.zoom=this._zoom;
	}
	
	this.zoom_out=function(){
		this._zoom_core(1/1.2);
	}
}

//-------------------------------------------------
//描画クラス
//-------------------------------------------------

function DrawCanvas(){
	//メンバ変数
	this._x_array;
	this._y_array;
	this._draw_flag=false;
	
	this.release_flag=function(){
		this._draw_flag=false;
	}
	
	this.on_mouse_move=function(x,y){
		this._draw(x,y);
	}
	
	this.on_mouse_down=function(x,y){
		this._x_array=new Array();
		this._y_array=new Array();
		this._x_array.push(this._get_mx(x));
		this._y_array.push(this._get_my(y));
		this._draw_flag=true;	
			
		can_drawing.style.opacity=g_alpha.get_alpha();
		
		g_undo_redo.push();
	}
	
	this.on_mouse_up=function(){
		if(this._draw_flag){
			if(this._x_array.length>=1){
				for(var i=0;i<2;i++){
					this._x_array.push(this._x_array[0]);
					this._y_array.push(this._y_array[0]);
				}
				this._draw_core();
			}
		}

		this._draw_flag=false;

		context=can_back.getContext("2d");
		context.globalAlpha=g_alpha.get_alpha();
		context.drawImage(can_drawing,0,0);

		context=can_drawing.getContext("2d");
		context.clearRect(0,0,can_drawing.width,can_drawing.height);
	}
	
	// 描画処理
	this._draw=function (x,y){
		if(!this._draw_flag){
			return;
		}
		
		this._x_array.push(this._get_mx(x));
		this._y_array.push(this._get_my(y));
		
		this._draw_core();
	}
	
	this._draw_core=function(){
		if(this._x_array.length<=2)
			return;

		var context = can_drawing.getContext("2d");
		context.strokeStyle = g_palette.get_color();
		context.lineWidth = g_pen_size.get_size();
		context.lineCap = "round";
		
		context.beginPath();
		context.moveTo(this._x_array[0], this._y_array[0]);
		context.quadraticCurveTo(this._x_array[1], this._y_array[1],this._x_array[2],this._y_array[2]);
		context.stroke();
		context.closePath();
		
		this._x_array.shift();
		this._y_array.shift();

		this._x_array.shift();
		this._y_array.shift();
	} 
	
	//描画位置
	this._get_mx=function(x){
		var canvasRect = can_drawing.getBoundingClientRect();
		return (x-canvasRect.left*g_hand.get_zoom())/g_hand.get_zoom();
	}
	
	this._get_my=function(y){
		var canvasRect = can_drawing.getBoundingClientRect();
		return (y-canvasRect.top*g_hand.get_zoom())/g_hand.get_zoom();
	}
	
	this.clear=function(){
		g_undo_redo.push();
		var context=can_back.getContext("2d");
		context.clearRect(0,0,can_drawing.width,can_drawing.height);
	}
}

//-------------------------------------------------
//アルファ
//-------------------------------------------------

function Alpha(){
	this._alpha_n=10;
	this._alpha=0;
	this._is_touch_mode=false;

	this.init=function(){
		this.update();
		this._on_click_core(this._alpha_n-1);
	}
	
	this.update=function(){
		var txt="";
		for(var i=0;i<this._alpha_n;i++){
			var color=g_palette.get_color();
			var alpha=((i+1)/this._alpha_n);
			txt+="<div id='alpha"+i+"' style='float:left;width:"+g_color_width+"px;height:"+g_color_width+"px;background-color:"+color+";opacity:"+alpha+";'";
			if(ipad_is_pc()){
				txt+=" onclick='javascript:g_alpha.on_click("+i+",false);'";
			}else{
				txt+=" ontouchstart='javascript:this.onclick=null;g_alpha.on_click("+i+",true);'";
			}
			txt+=">";
			txt+="</div>";
		}
		document.getElementById("alpha").innerHTML=txt;

		if(!ipad_is_pc()){
            for(var i=0;i<this._alpha_n;i++){
                document.getElementById("alpha"+i).addEventListener("touchstart", function(){g_alpha.on_click(Number(this.id.split("alpha")[1]),true);},false);
            }
        }

		this._on_click_core(this._alpha);
	}
	
	this.on_click=function(i,is_touch){
//		if(ipad_onclick_prevent(is_touch))
//			return;
		this._on_click_core(i);
	}
	
	this._on_click_core=function(i){
		this._alpha=i;

		for(var i=0;i<this._alpha_n;i++){
			var w=g_color_width;
			var h=g_color_width;
			if(i==this._alpha){
				w=g_color_width-8;
				h=g_color_width-8;
				var color="#ffffff";
				if(g_palette.get_color()=="#ffffff"){
					color="#aaaaaa";
				}
				document.getElementById("alpha"+i).style.border="solid 4px "+color;
			}else{
				document.getElementById("alpha"+i).style.border="none";
			}
			document.getElementById("alpha"+i).style.width=w;
			document.getElementById("alpha"+i).style.height=h;
		}
	}
	
	this.get_alpha=function(){
		return (this._alpha+1)/this._alpha_n;
	}
	
	this.get_alpha_no=function(){
		return this._alpha;
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
//		if(ipad_onclick_prevent(is_touch))
//			return;
		
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
			}else{
//				txt+=" ontouchstart='javascript:this.onclick=null;g_palette.on_click("+i+",true);'";
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
		return this._color;
	}
}

//-------------------------------------------------
//ツールボックス
//-------------------------------------------------

function ToolBox(){
	this._add_button=function(cmd,info,s,margin){
		var button_style="margin:2px;float:left;text-align:center;width:"+s+"px;height:"+s+"px;border:solid 1px #cccccc;";
		var txt='<div id="'+cmd+'"';
		if(ipad_is_pc()){
			txt+=' onclick="javascript:'+cmd+'(false);"';
		}else{
			//txt+=' ontouchstart="javascript:this.onclick=null;'+cmd+'(true);"';
		}
		txt+=' style="'+button_style+'margin-left:'+margin+'px;">'+info+'</div>';
		return txt;
	}
	
	this.init=function(){
		var txt="";
		var s=g_button_width+20;
		var margin=6;
		txt+=this._add_button("ipad_switch_palette_form","パレット",s,margin);
		txt+=this._add_button("ipad_switch_pen_form","ペン",s,0);
		txt+=this._add_button("g_undo_redo.undo","元に戻す",s,margin);
		txt+=this._add_button("g_undo_redo.redo","やり直す",s,0);
		txt+=this._add_button("g_hand.zoom_out","縮小",s,margin);
		txt+=this._add_button("g_hand.zoom_in","拡大",s,0);
		txt+=this._add_button("g_draw_canvas.clear","クリア",s,margin);
		txt+=this._add_button("ipad_switch_upload_form","投稿",s,margin);
		document.getElementById("toolmenu").innerHTML=txt+"<br clear='both'>";

        //遅延登録が必須
		if(!ipad_is_pc()){
            document.getElementById("ipad_switch_palette_form").addEventListener("touchstart", function(e){ipad_switch_palette_form(true);},false);
            document.getElementById("ipad_switch_pen_form").addEventListener("touchstart", function(e){ipad_switch_pen_form(true);},false);
            document.getElementById("g_undo_redo.undo").addEventListener("touchstart", function(e){g_undo_redo.undo(true);},false);
            document.getElementById("g_undo_redo.redo").addEventListener("touchstart", function(e){g_undo_redo.redo(true);},false);
            document.getElementById("g_hand.zoom_out").addEventListener("touchstart", function(e){g_hand.zoom_out(true);},false);
            document.getElementById("g_hand.zoom_in").addEventListener("touchstart", function(e){g_hand.zoom_in(true);},false);
            document.getElementById("g_draw_canvas.clear").addEventListener("touchstart", function(e){g_draw_canvas.clear(true);},false);
            document.getElementById("ipad_switch_upload_form").addEventListener("touchstart", function(e){ipad_switch_upload_form(true);},false);
        }
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
		var s=g_button_width+20;
		for(var i=1;i<this._n;i++){
			var r=i*i/2+1;
			if(r>s/2){
				r=s/2;
			}
			txt+="<div id='pensize"+i+"' style='float:left;width:"+s+"px;height:"+s+"px;' ";
			if(ipad_is_pc()){
				txt+="onclick='javascript:g_pen_size.on_click("+i+")' ";
			}else{
				//txt+="ontouchstart='javascript:this.onclick=null;g_pen_size.on_click("+i+")' ";
			}
			txt+=">";
			txt+="<div style='margin:auto;margin-top:"+(s-r*2)/2+"px;width: "+(r*2)+"px;height: "+(r*2)+"px;background: black;-moz-border-radius: "+r+"px;-webkit-border-radius: "+r+"px;border-radius: "+r+"px;'></div>";
			txt+="</div>";
		}
		document.getElementById("pensize_form").innerHTML=txt+"<br clear='both'>";

		if(!ipad_is_pc()){
            for(var i=1;i<this._n;i++){
                document.getElementById("pensize"+i).addEventListener("touchstart", function(){g_pen_size.on_click(this.id.split("pensize")[1]);},false);
            }
        }
        
		this.on_click(2);
	}
	
	this.on_click=function(s){
		this._size=(s*s/2+1)*2;
		for(var i=1;i<this._n;i++){
			if(i==s){
				document.getElementById("pensize"+i).style.background="#cccccc";
			}else{
				document.getElementById("pensize"+i).style.background="none";
			}
		}
	}

	this.get_size=function (){
		return this._size;
	}
}

//-------------------------------------------------
//UNDO
//-------------------------------------------------

function UndoRedo(){
	this._undo_array=new Array();
	this._redo_array=new Array();
	
	this._get_now_image=function(){
		var image_data = can_back.getContext("2d").getImageData(0,0,can_back.width, can_back.height);
		return image_data;
	}

	this.push=function(){
		this._undo_array.push(this._get_now_image());
		this._redo_array=new Array();
		while(this._undo_array.length>=16){
			this._undo_array.shift();
		}
	}

	this.undo=function(is_touch){
//		if(ipad_onclick_prevent(is_touch))
//			return;
		if(this._undo_array.length<=0)
			return false;
		this._redo_array.push(this._get_now_image());
		var image_data=this._undo_array.pop();
		can_back.getContext("2d").putImageData(image_data,0,0);
		return false;
	}
	
	this.redo=function(is_touch){
//		if(ipad_onclick_prevent(is_touch))
//			return;
		if(this._redo_array.length<=0)
			return false;
		this._undo_array.push(this._get_now_image());
		var image_data=this._redo_array.pop();
		can_back.getContext("2d").putImageData(image_data,0,0);
		return false;
	}
}

//-------------------------------------------------
//画像送信
//-------------------------------------------------

function Upload(){
	this._boundary = "-----boundary_illustbook_ipad";
	this._data;
	
	this._bbs_key;
	this._thread_key;
	this._reply;
	
	this._append=function(tag,data){
		//this._data+=""+tag+"="+data+"&";
		this._data += "--"+this._boundary+"\r\n"+"Content-Disposition: form-data; name=\""+tag+"\"\r\n\r\n"+ data+"\r\n";
	}
	
	this._header_split=function(data){
		//'data:image/png;base64,iVBORw0K...'の「,」以降のデータを取得してそれをデコードする
		return data.split(",")[1];
	}
	
	this.upload=function(bbs_key,thread_key,reply){
		this._bbs_key=bbs_key;
		this._thread_key=thread_key;
		this._reply=reply;
	
		this._create_thumbnail();
	
		var title=document.getElementById("title").value;
		var author=document.getElementById("name").value;
		var comment=document.getElementById("comment").value;
		var delete_key=document.getElementById("delete_key").value;
		
		if(title==""){
			title="notitle";
		}
		if(author==""){
			alert("投稿者名は必須です。");
			return;
			//author="unknown";
		}

		var expires = "Thu, 1-Jan-2030 00:00:00 GMT";
		//var domain = location.hostname.replace(/^[^\.]*/, "");
		document.cookie="name="+escape(author)+"; expires="+expires;// domain="+domain+"; expirse="+expires;

		alert("画像をアップロードします。OKを押した後、しばらくお待ちください。");
		
		title=(title)
		author=(author)
		comment=(comment)
		delete_key=(delete_key)
	
		this._data="";
		this._append("bbs_key",bbs_key);
		if(reply=="1"){
			this._append("thread_key",thread_key);
			this._append("reply","1");
		}
		this._append("thread_title",title);
		this._append("homepage_addr","");
		this._append("author",author);
		this._append("comment",comment);
		this._append("delete_key",delete_key);
		this._append("illust_mode","1");
		this._append("mode","illust_all");
		this._append("base64","1");

        link_to_profile=document.getElementById("link_to_profile")
        if(link_to_profile && link_to_profile.checked){
            this._append("link_to_profile","on");
        }

		var thumbnail_can=document.getElementById("canvas_thumbnail");
		var thumbnail = this._header_split(thumbnail_can.toDataURL("image/jpeg",0.95));
		var image = this._header_split(can_back.toDataURL("image/jpeg"));

		this._append("thumbnail",thumbnail);
		this._append("image",image);

		this._data += "--"+this._boundary+"--\r\n";
		
		//alert(this._data);
		
		var cmd="upl_all";
		if(reply){
			cmd="add_entry";
		}
	
		this.requestFile(this._data,"POST",cmd,false,ipad_upload_callback);
	}
	
	this.requestFile=function ( data , method , fileName , async ,callback_function){
		var httpoj = new XMLHttpRequest()
		httpoj.open( method , fileName , async )
		httpoj.onreadystatechange = function()
		{ 
			if (httpoj.readyState==4)
			{ 
				callback_function(httpoj)
			}
		}
		httpoj.setRequestHeader("content-type","multipart/form-data; boundary="+this._boundary);
		httpoj.send( data )
	}
	
	this.go_bbs=function(oj){
		var url_text="bbs_index?bbs_key="+this._bbs_key
		if(this._reply=="1"){
			url_text="usr/"+this._bbs_key+"/"+this._thread_key+".html";
		}
		window.location.href=url_text;
	}

	this._avg=function(src,fx,fy,mx,my,rgb){
		var ix=Math.floor(fx);
		var iy=Math.floor(fy);
		fx-=ix;
		fy-=iy;
		
		var sum=0;
		var cnt=0;
		for(var y=0;y<my;y++){
			for(var x=0;x<mx;x++){
				sum+=src.data[(iy+y)*can_back.width*4+(ix+x)*4+rgb];
				cnt++;
			}
		}
		
		return sum/cnt;
	}
	
	//平均画素法で高品質のサムネイルを作成
	this._create_thumbnail=function(){
		var thumbnail_can=document.getElementById("canvas_thumbnail");
		var image_data=thumbnail_can.getContext("2d").createImageData(thumbnail_can.width,thumbnail_can.height);
		var src=can_back.getContext("2d").getImageData(0,0,can_back.width,can_back.height);

		var mx=can_back.width/thumbnail_can.width;
		var my=can_back.height/thumbnail_can.height;
		
		if(mx<my){
			mx=my;
		}else{
			my=mx;
		}
		
		ox=Math.floor((100-can_back.width/mx)/2);
		oy=Math.floor((100-can_back.height/my)/2)
		
		for(var y=0;y<can_back.height/my;y++){
			for(var x=0;x<can_back.width/mx;x++){
				var fx=x*mx;
				var fy=y*my;
				for(var rgb=0;rgb<4;rgb++){
					image_data.data[(y+oy)*thumbnail_can.width*4+(x+ox)*4+rgb]=this._avg(src,fx,fy,mx,my,rgb);
				}
			}
		}
		thumbnail_can.getContext("2d").putImageData(image_data,0,0);
	}
}
