//-------------------------------------------------
//イラブペイント　UNDO
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

var UNDO_MAX=16;

function UndoRedo(){
	this._undo_array=new Array();
	this._redo_array=new Array();
	
	this._get_now_image=function(layer){
		var image_data = can_fixed[layer].getContext("2d").getImageData(0,0,can_fixed[layer].width, can_fixed[layer].height);
		return image_data;
	}

	this.push=function(){
		if(g_chat.is_chat_mode()){
			g_buffer.redo_clear();
			return;
		}
		var layer=g_layer.get_layer_no();
		var obj=new Object();
		obj.layer=layer;
		obj.image=this._get_now_image(layer);
		this._undo_array.push(obj);
		this._redo_array=new Array();
		while(this._undo_array.length>=UNDO_MAX){
			this._undo_array.shift();
		}
	}

	this.undo=function(is_touch){
		if(g_chat.is_chat_mode()){
			g_buffer.undo();
			return false;
		}
		if(this._undo_array.length<=0){
			return false;
		}
		var obj=this._undo_array.pop();
		var layer=obj.layer;

		var redo_obj=new Object();
		redo_obj.layer=layer;
		redo_obj.image=this._get_now_image(layer);
		
		this._redo_array.push(redo_obj);

		can_fixed[obj.layer].getContext("2d").putImageData(obj.image,0,0);
		g_buffer.undo_redo_exec_on_local_tool();

		return false;
	}
	
	this.redo=function(is_touch){
		if(g_chat.is_chat_mode()){
			g_buffer.redo();
			return false;
		}
		if(this._redo_array.length<=0){
			return false;
		}

		var obj=this._redo_array.pop();
		var layer=obj.layer;

		var undo_obj=new Object();
		undo_obj.layer=layer;
		undo_obj.image=this._get_now_image(layer);

		this._undo_array.push(undo_obj);
		
		can_fixed[obj.layer].getContext("2d").putImageData(obj.image,0,0);
		g_buffer.undo_redo_exec_on_local_tool();
		
		return false;
	}
}
