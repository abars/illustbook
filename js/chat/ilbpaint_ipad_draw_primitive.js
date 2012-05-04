//-------------------------------------------------
//イラブペイント　プリミティブ描画
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

function DrawPrimitive(){
	this.init=function(){
	}
	
	this.clear=function(canvas){
		var context=canvas.getContext("2d");
		context.clearRect(0,0,canvas.width,canvas.height);
	}
}
