//--------------------------------------------------------
//リッチテキストエディタ
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

//--------------------------------------------------------
//public API
//--------------------------------------------------------

function rediter_init(id,initial_text,fontsize,enable_tag_edit){
	if(!initial_text){ initial_text=""; }
	if(!id){ id='rediter'; }

	rediter_set(id,initial_text,fontsize);
	rediter_create_palette(id);
	rediter_create_fontsize(id);
	rediter_create_button(id,enable_tag_edit);
}

function rediter_get_text(id){
	if(!id){
		id="rediter";
	}
	if(rediter_get_iframe_element(id).style.display=="none"){
		return rediter_get_tag_editer_element(id).value;
	}
	return rediter_get_iframe(id).body.innerHTML;
}

//--------------------------------------------------------
//initialize
//--------------------------------------------------------

function rediter_get_iframe_element(id){
	return document.getElementById(id+"_iframe");
}

function rediter_get_tag_editer_element(id){
	return document.getElementById(id+"_tag");
}

function rediter_get_iframe(id){
	var doc;
	var iframe = rediter_get_iframe_element(id);
	if(iframe.contentWindow){
		doc = iframe.contentWindow.document;
	}else{
		doc = iframe.contentDocument; 
	}
	return doc;
}

function rediter_set(id,initial_text,fontsize){
	var doc=rediter_get_iframe(id);
	doc.designMode = 'on';
	doc.open();
	doc.write('<html><head><style>body{font-size:'+fontsize+';}p{margin:0px;}</style></head><body></body></html>');
	//marginはIEのダブル改行対策
	doc.close();
	
	//初期テキスト
	doc.body.innerHTML=initial_text;
}

var rediter_color=new Array();

function rediter_create_palette(id){
	var palette=document.getElementById(id+"_palette");
	var text="";
	rediter_color[0]="000000";
	rediter_color[1]="c0c0c0";
	rediter_color[2]="ff0000";
	rediter_color[3]="ffff00";
	rediter_color[4]="00ff00";
	rediter_color[5]="00ffff";
	rediter_color[6]="0000ff";
	rediter_color[7]="ff00ff";
	rediter_color[8]="ff0000";
	rediter_color[8]="ffffff";
	for(var i=0;i<9;i++){
		text+="<button onClick='rediter_change_color("+i+",\""+id+"\")' style='border:0px;padding:1px;'>";
		text+="<div style='width:14px;height:14px;padding:0px;margin:0px;background-color:#"+rediter_color[i];
		text+=";float:left;'</div>";
		text+="</button>";
	}
	palette.innerHTML=text;
}

function rediter_create_fontsize(id){
	var fontsize=document.getElementById(id+"_fontsize");
	var text="";
	text+='<select onChange="rediter_change_fontsize(this,\''+id+'\');">';
	text+='<option value="3">文字サイズ</option>';
	text+='<option value="1">1</option>';
	text+='<option value="2">2</option>';
	text+='<option value="3">3</option>';
	text+='<option value="4">4</option>';
	text+='<option value="5">5</option>';
	text+='</select>';
	fontsize.innerHTML=text;
}

function rediter_create_button(id,enable_tag_edit){
	var button=document.getElementById(id+"_button");
	var text="<div class='g-button-group'>";
	text+='<button class="g-button" onClick="rediter_bold(\''+id+'\');">強調</button>';
    text+='<button class="g-button" onClick="rediter_link(\''+id+'\');">リンク</button>';
	text+='<button class="g-button" onClick="rediter_remove_format(\''+id+'\');">クリア</button>';
	if(enable_tag_edit){
		text+='<button class="g-button" onClick="rediter_switch_edit_mode(\''+id+'\');">タグ編集</button>';
	}
	text+="</div>";
	button.innerHTML=text;
}

//--------------------------------------------------------
//Event
//--------------------------------------------------------

function rediter_change_color(color_no,id){
	var doc=rediter_get_iframe(id);
	doc.execCommand( "forecolor", false, rediter_color[color_no] );
}

function rediter_change_fontsize(font,id){
	var size=font.options[font.selectedIndex].value;
	var doc=rediter_get_iframe(id);
	doc.execCommand("fontsize",false,size);
}

function rediter_bold(id){
	var doc=rediter_get_iframe(id);
	doc.execCommand("bold",false,false);
}

function rediter_remove_format(id){
	var doc=rediter_get_iframe(id);
	doc.execCommand("removeformat",false,false);
	doc.execCommand("Unlink",false,false);
}

function rediter_link(id){
	var doc=rediter_get_iframe(id);
	var szURL = prompt("リンク先のURLを入力：", "http://");
	if ((szURL != null) && (szURL != "")) {
		doc.execCommand("CreateLink",false,szURL);
	}
}

function rediter_switch_edit_mode(id){
	//switch
	var iframe = rediter_get_iframe_element(id);
	var tag=rediter_get_tag_editer_element(id);
	if(iframe.style.display=="none"){
		iframe.style.display="block";
		tag.style.display="none";
		rediter_get_iframe(id).body.innerHTML=tag.value;
	}else{
		iframe.style.display="none";
		tag.style.display="block";
		tag.value=rediter_get_iframe(id).body.innerHTML;
	}
}
