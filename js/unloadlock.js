//--------------------------------------------------------
//保存せずにページを移動しようとした場合に警告する
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

var unload_event_check_need=false;

//画像を編集したら呼び出してダイアログを出すようにする
function NeedUnloadCheck(){
	unload_event_check_need=true;
}

//保存に成功したら呼び出してダイアログを出さないようにする
function NoNeedUnloadCheck(){
	unload_event_check_need=false;
}

//保存せずに移動しようとしたらダイアログを出す
window.onbeforeunload = function (evt) { 
	if(!unload_event_check_need)
		return;
	var message = '編集を破棄して、このページから移動します。よろしいですか？';
	if (typeof evt == 'undefined') {//IE 
		evt = window.event; 
	}
	if (evt) { 
		evt.returnValue = message; 
	}
	return message; 
}

