//------------------------------------------------
//インスタンス化
//------------------------------------------------

var illustbook=Object();
illustbook.request=new illustbook_request();
illustbook.user=new illustbook_user();
illustbook.utility=new illustbook_utility();
illustbook.app=new illustbook_app();
illustbook.canvas=illustbook_canvas;
illustbook.perpetuation=new illustbook_perpetuation();
illustbook.bookmark=new illustbook_bookmark();
illustbook.feed=new illustbook_feed();

//------------------------------------------------
//request api
//------------------------------------------------

function illustbook_request(){
	this._boundary = "-----boundary_illustbook_api";
}
	
illustbook_request.prototype._create_http_request=function(){
	if(window.ActiveXObject){
		try {
			return new ActiveXObject("Msxml2.XMLHTTP")
		} catch (e) {
			try {
				return new ActiveXObject("Microsoft.XMLHTTP")
			} catch (e2) {
				return null
			}
		}
	} else if(window.XMLHttpRequest){
		return new XMLHttpRequest()
	} else {
		return null
	}
}

illustbook_request.prototype._request_file=function( data , method , fileName , async ,callback_function){
	var httpoj = this._create_http_request()
	httpoj.open( method , fileName , async )
	httpoj.onreadystatechange = function()
	{ 
		if (httpoj.readyState==4)
		{ 
			callback_function(httpoj)
		}
	}
	if(method=="POST"){
		httpoj.setRequestHeader("content-type","multipart/form-data; boundary="+this._boundary);
	}
	httpoj.send( data )
}

illustbook_request.prototype._is_same_domain=function(url){
	if(location.host.match(/www\.illustbook\.net/)){
		return true;
	}
	if(location.host.match(/localhost:8084/)){
		return true;
	}
	if(url.match(/^\.\//)){
		return true;
	}
	return false;
}

illustbook_request.prototype.get=function(url,callback){
	if(!illustbook.request._is_same_domain(url)){
		illustbook.request._getJSON(url,callback);
		return;
	}
	this._request_file("","GET",url,true,
		function(oj) {
			var txt=oj.responseText;
			callback(eval("("+txt+")"));
		}
	);
}

illustbook_request.prototype.post=function(url,obj,callback){
	this._post_core(url,obj,callback,false);
}

illustbook_request.prototype.post_async=function(url,obj,callback){
	this._post_core(url,obj,callback,true);
}

illustbook_request.prototype._post_core=function(url,obj,callback,async){
	var code="";
	code="";
	for(tag in obj){
		var data=obj[tag];
		code += "--"+this._boundary+"\r\n"+"Content-Disposition: form-data; name=\""+tag+"\"\r\n\r\n"+ data+"\r\n";
	}
	code += "--"+this._boundary+"--\r\n";
	this._request_file(code,"POST",url,async,function(oj){
			var txt=oj.responseText;
			callback(eval("("+txt+")"));
		}
	);
}

illustbook_request.prototype._getJSON=function(url,callback){
	url=url+"&callback="+callback.toString().match(/^function ([^(]+)/)[1];//
	//callback.name doesnt work in IE
	var target = document.createElement('script'); 
	target.charset = 'utf-8';  
	target.src = url;
	document.body.appendChild(target);  
}

illustbook_request.prototype._getObject=function(api_class,api_method,bbs_id,user_id,offset,limit,order,callback){
	var api_args="offset="+offset+"&limit="+limit;
	if(order){
		api_args+="&order="+order;
	}
	if(bbs_id){
		api_args+="&bbs_id="+bbs_id;
	}
	if(user_id){
		api_args+="&user_id="+user_id;
	}
	if(illustbook_request.prototype._is_packed_request){
		illustbook_request.prototype._request_args+="class="+api_class+"&method="+api_method+"&"+api_args+":";
		illustbook_request.prototype._request_callback.push(callback);
	}else{
		var url=api_class+"?method="+api_method+"&"+api_args;
		illustbook.request.get("{{host}}"+url,callback);
	}
}

//------------------------------------------------
//packed request api
//------------------------------------------------

illustbook_request.prototype._is_packed_request=false;

//beginPackedRequest〜endPackedRequestの区間に呼ばれたAPIを、1度のHTTPリクエストで実行します。
//非公開APIです。

illustbook_request.prototype.beginPackedRequest=function(){
	illustbook_request.prototype._is_packed_request=true;
	illustbook_request.prototype._request_args="";
	illustbook_request.prototype._request_callback=new Array();
}

illustbook_request.prototype.endPackedRequest=function(){
	illustbook_request.prototype._is_packed_request=false;
	var url="{{host}}api_packed?"+illustbook_request.prototype._request_args;
	illustbook.request.get(url,illustbook_request.prototype.callbackPackedRequest);
}

illustbook_request.prototype.callbackPackedRequest=function(oj){
	for(var i=0;i<illustbook_request.prototype._request_callback.length;i++){
		var callback=illustbook_request.prototype._request_callback[i];
		callback(oj["request"+i]);
	}
}

//------------------------------------------------
//user api
//------------------------------------------------

function illustbook_user(){
	this._user_id="{{user_id}}";
	this.ORDER_NONE=null;
}

illustbook_user.prototype.getCurrentUser=function(){
	return this._user_id;
}

illustbook_user.prototype.getOwner=function(){
	return illustbook.utility.getUrlArg()["user_id"];
}

illustbook_user.prototype.getBbsList=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_user","getBbsList",null,user_id,offset,limit,order,callback);
}

illustbook_user.prototype.getThreadList=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_user","getThreadList",null,user_id,offset,limit,order,callback);
}

illustbook_user.prototype.getTimeline=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_user","getTimeline",null,user_id,offset,limit,order,callback);
}

illustbook_user.prototype.getFollow=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_user","getFollow",null,user_id,offset,limit,order,callback);
}

illustbook_user.prototype.getFollower=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_user","getFollower",null,user_id,offset,limit,order,callback);
}

illustbook_user.prototype.getFollowFast=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_user","getFollowFast",null,user_id,offset,limit,order,callback);
}

illustbook_user.prototype.getFollowerFast=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_user","getFollowerFast",null,user_id,offset,limit,order,callback);
}

//------------------------------------------------
//utility api
//------------------------------------------------

function illustbook_utility(){
	this._tmp=0;
}

illustbook_utility.prototype.getUrlArg=function(){
	var arg = new Object();
	var pair=location.search.substring(1).split('&');
	for(i=0;pair[i];i++) {
		var kv = pair[i].split('=');
		arg[kv[0]]=kv[1];
	}
	return arg;
}

illustbook_utility.prototype.createCallback=function(class_obj,func_name){
	return (function(obj,func){return function(e){obj[func](e)}})(class_obj,func_name);
}

//------------------------------------------------
//app api
//------------------------------------------------

function illustbook_app(){
	this._app_list=new Array();
	this._app_id_list=new Array();
}

illustbook_app.prototype.regist=function(my_app){
	//add app object
	var app_id="app_"+this._app_list.length;
	this._app_list.push(my_app);
	this._app_id_list.push(app_id);
	var app_div=document.getElementById("illustbook_app");
	var new_div="<div id='"+app_id+"'>アプリを読み込み中</div>";
	app_div.innerHTML+=new_div
	my_app._app_id=app_id;

	//wait for canvas initialize
	//my_app.init();
	init_callback=illustbook.utility.createCallback(my_app,"init");
	if (window.addEventListener) { //for W3C DOM
		window.addEventListener("load", init_callback, false);
	} else if (window.attachEvent) { //for IE
		window.attachEvent("onload", init_callback);
	} else  {
		window.onload = init_callback;
	}
}

illustbook_app.prototype.remove_all=function(){
	var app_div=document.getElementById("illustbook_app");
	app_div.innerHTML="";
	this._app_list=new Array();
	this._app_id_list=new Array();
}

illustbook_app.prototype.addLoopCallback=function(my_app,interval){
	setInterval(illustbook.utility.createCallback(my_app,"loop"),interval);
}

illustbook_app.prototype.getAppKey=function(){
	return "{{app_key}}";	
}

illustbook_app.prototype.getDiv=function(my_app){
	return document.getElementById(my_app._app_id);
}


illustbook_utility.prototype.addEvent=function(obj, type, func){
	if(obj.addEventListener){
		//Webkit
		obj.addEventListener(type, func, false);
	}else{
		if(obj.attachEvent){
			//IE
			obj.attachEvent('on' + type, func);
		}
	}
}

//------------------------------------------------
//canvas api
//------------------------------------------------

function illustbook_canvas(my_app,width,height){
	this._callback_app=null;
	this._app_id=my_app._app_id;
	
	if(width && height){
		this.width=width;
		this.height=height;
	}else{
		this.width=160;
		this.height=160;
	}
	
	this._canvas=null;
	this._ctx=null;
	this._init(my_app);
}

illustbook_canvas.prototype._init=function(my_app){
	document.getElementById(this._app_id).innerHTML="<canvas id='canvas_"+this._app_id+"' width='"+this.width+"' height='"+this.height+"'></canvas>";
	this._canvas=document.getElementById("canvas_"+this._app_id);
	
	//initializa flash canvas
	if (typeof FlashCanvas != "undefined") {
		FlashCanvas.initElement(this._canvas);
	}

	this._ctx = this._canvas.getContext('2d');
}

illustbook_canvas.prototype.drawBegin=function(){
	this._ctx.save();
}

illustbook_canvas.prototype.drawEnd=function(){
	this._ctx.restore();
}

illustbook_canvas.prototype._get_color=function(dec) {
	var hex = "#";
	for(var j=0;j<6;j++){
		var last = (dec>>20) & 15;
		hex += String.fromCharCode(((last>9)?55:48)+last);
		dec <<= 4;
	}
	return hex;
}


illustbook_canvas.prototype.fillRect=function(x,y,w,h,color){
	this._ctx.fillStyle=this._get_color(color);
	this._ctx.fillRect(x, y, w, h)
}

illustbook_canvas.prototype.drawString=function(x,y,txt,size,color){
}

illustbook_canvas.prototype.addTouchCallback=function(my_app){
	this._callback_app=my_app;
	if({{is_mobile}}){
		illustbook.utility.addEvent(this._canvas,"touchstart",illustbook.utility.createCallback(this,"_on_touch_start"));
		illustbook.utility.addEvent(this._canvas,"touchmove",illustbook.utility.createCallback(this,"_on_touch_move"));
		illustbook.utility.addEvent(this._canvas,"touchend",illustbook.utility.createCallback(this,"_on_touch_end"));
	}else{
		illustbook.utility.addEvent(this._canvas,"mousedown",illustbook.utility.createCallback(this,"_on_mouse_down"));
		illustbook.utility.addEvent(this._canvas,"mousemove",illustbook.utility.createCallback(this,"_on_mouse_move"));
		illustbook.utility.addEvent(this._canvas,"mouseup",illustbook.utility.createCallback(this,"_on_mouse_up"));
	}
}

illustbook_canvas.prototype._on_touch_start=function(evt){
	var canvasRect = this._canvas.getBoundingClientRect();
	this._callback_app.onTouchStart(evt.touches[0].clientX-canvasRect.left,evt.touches[0].clientY-canvasRect.top);
	this._prevent_default(evt);
}

illustbook_canvas.prototype._on_touch_move=function(evt){
	var canvasRect = this._canvas.getBoundingClientRect();
	this._callback_app.onTouchMove(evt.touches[0].clientX-canvasRect.left,evt.touches[0].clientY-canvasRect.top);
	this._prevent_default(evt);
}

illustbook_canvas.prototype._on_touch_end=function(evt){
	this._callback_app.onTouchEnd();
	this._prevent_default(evt);
}

illustbook_canvas.prototype._get_mouse_pos=function(evt){
	var x=evt.clientX-this._canvas.offsetLeft;
	var y=evt.clientY-this._canvas.offsetTop;
	x+=(document.documentElement.scrollLeft || document.body.scrollLeft);
	y+=(document.documentElement.scrollTop || document.body.scrollTop);
	return {"x":x,"y":y};
}

illustbook_canvas.prototype._on_mouse_down=function(evt){
	var pos=this._get_mouse_pos(evt);
	this._callback_app.onTouchStart(pos.x,pos.y);
	this._prevent_default(evt);
}

illustbook_canvas.prototype._on_mouse_move=function(evt){
	var pos=this._get_mouse_pos(evt);
	this._callback_app.onTouchMove(pos.x,pos.y);
	this._prevent_default(evt);
}

illustbook_canvas.prototype._on_mouse_up=function(evt){
	this._callback_app.onTouchEnd();
	this._prevent_default(evt);
}

illustbook_canvas.prototype._prevent_default=function(evt){
	if(evt.preventDefault){
		evt.preventDefault();
	}else{
		evt.returnValue = false;
	}
}

illustbook_canvas.prototype.loadImage=function(url){
	//Flashcanvasのsamedomainチェックはhttpを含んでいるかで行なっているため、
	//同じドメインの場合はURLを置換する
	//samedomainでない場合はproxy.phpが呼び出されるがGAEには置けない
	url=url.replace("{{host}}","./");
	var img = new Image();
	img.src=url;
	return img;
}

illustbook_canvas.prototype.drawImage=function(img,x,y){
	this._ctx.drawImage(img,x,y);
}

illustbook_canvas.prototype.drawImageRect=function(img,sx,sy,sw,sh,dx,dy,dw,dh){
	this._ctx.drawImage(img,sx,sy,sw,sh,dx,dy,dw,dh);
}

illustbook_canvas.prototype.drawText=function(text,x,y,font_size,color){
	this._ctx.font = ""+font_size+"pt Arial";
	this._ctx.fillStyle = this._get_color(color);
	this._ctx.fillText(text,x,y+font_size+4);
}

//------------------------------------------------
//perpetuation api
//------------------------------------------------

function illustbook_perpetuation(){
	this._tmp=0;
}

illustbook_perpetuation.prototype.getData=function(data_key,callback){
	var user_id=illustbook.user.getCurrentUser();
	var app_key=illustbook.app.getAppKey();
	var args="app_key="+app_key+"&user_id="+user_id+"&data_key="+data_key;
	illustbook.request.get("api_perpetuation?method=getData&"+args,callback);
}

illustbook_perpetuation.prototype.putData=function(data_key,int_data,text_data,callback){
	var data_obj=[];
	data_obj.int_data=int_data;
	data_obj.text_data=text_data;
	app_key=illustbook.app.getAppKey();
	user_id=illustbook.user.getCurrentUser();
	var args="app_key="+app_key+"&user_id="+user_id+"&data_key="+data_key;
	illustbook.request.post("api_perpetuation?method=putData&"+args,data_obj,callback);
}

//------------------------------------------------
//bookmark api
//------------------------------------------------

function illustbook_bookmark(){
	this.ORDER_NONE=null;
}

illustbook_bookmark.prototype.getThreadList=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_bookmark","getThreadList",null,user_id,offset,limit,order,callback);
}

illustbook_bookmark.prototype.getBbsList=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_bookmark","getBbsList",null,user_id,offset,limit,order,callback);
}

illustbook_bookmark.prototype.getAppList=function(user_id,offset,limit,order,callback){
	illustbook.request._getObject("api_bookmark","getAppList",null,user_id,offset,limit,order,callback);
}

//------------------------------------------------
//feed api
//------------------------------------------------

function illustbook_feed(){
	this.ORDER_NEW="new";
	this.ORDER_MOPER="moper";
	this.ORDER_APPLAUSE="applause";
}

illustbook_feed.prototype.getThreadList=function(bbs_id,offset,limit,order,callback){
	illustbook.request._getObject("api_feed","getThreadList",bbs_id,null,offset,limit,order,callback);
}

