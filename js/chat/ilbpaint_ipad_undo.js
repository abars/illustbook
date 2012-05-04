//-------------------------------------------------
//イラブペイント　UNDO
//copyright 2010-2012 ABARS all rights reserved.
//-------------------------------------------------

function UndoRedo(){
	this._undo_array=new Array();
	this._redo_array=new Array();
	
	this._get_now_image=function(){
		var image_data = can_fixed.getContext("2d").getImageData(0,0,can_fixed.width, can_fixed.height);
		return image_data;
	}

	this.push=function(){
		if(g_chat.is_chat_mode()){
			return;	//チャットモードではUNDOできない
		}
		this._undo_array.push(this._get_now_image());
		this._redo_array=new Array();
		while(this._undo_array.length>=16){
			this._undo_array.shift();
		}
	}

	this.undo=function(is_touch){
		if(this._undo_array.length<=0)
			return false;
		this._redo_array.push(this._get_now_image());
		var image_data=this._undo_array.pop();
		can_fixed.getContext("2d").putImageData(image_data,0,0);
		return false;
	}
	
	this.redo=function(is_touch){
		if(this._redo_array.length<=0)
			return false;
		this._undo_array.push(this._get_now_image());
		var image_data=this._redo_array.pop();
		can_fixed.getContext("2d").putImageData(image_data,0,0);
		return false;
	}
}
