//--------------------------------------------------------
//イラストアップロードスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

	function uploadImage(overwrite){
		var ret=new Object();
		ret.name=document.getElementById("name").value;
		ret.comment=rediter_get_text();
		ret.adr=document.getElementById("homepage_addr").value;
		if(document.getElementById("title"))
			ret.title=document.getElementById("title").value;
		else
			ret.title="　";
		ret.category=document.getElementById("category").value
		if(ret.category=="add"){
			ret.category=document.getElementById("category_new").value
		}
		ret.event_id=document.getElementById("event_id").value
		ret.regulation=document.getElementById("regulation").value;
		ret.delete_key=document.getElementById("delete_key").value;
		ret.no_illust=document.getElementById("no_illust").checked;
		ret.dont_show_in_portal=document.getElementById("dont_show_in_portal").checked;

		var link_to_profile=document.getElementById("link_to_profile");
		if(link_to_profile && link_to_profile.checked){
			ret.link_to_profile="on";
		}else{
			ret.link_to_profile=false;
		}
		
		var resize_width=document.getElementById("resize_width");
		if(resize_width && resize_width.checked){
			flex_object=GetFlexObject();
			flex_object.SetResizeWidth(700);
		}
		
		var expires = "Thu, 1-Jan-2030 00:00:00 GMT";
		document.cookie="name="+escape(ret.name)+"; expires="+expires;
		document.cookie="adr="+escape(ret.adr)+"; expires="+expires;
		
		flex_object=GetFlexObject();
		if(overwrite)
			flex_object.OverwriteImage(ret);
		else
			flex_object.UploadImage(ret);
	}
	
	function GetFlexObject(){
		var flex_object;
		if (navigator.appName.indexOf("Microsoft") != -1 && !document["fromJavaScript"]) {
			flex_object=window["fromJavaScript"];
		} else {
			flex_object=document["fromJavaScript"];
		}
		return flex_object;
	}
	
	function SetToAlphaPngMode(){
		flex_object=GetFlexObject();
		flex_object.SetToAlphaPngMode(document.getElementById("alpha_png_mode").checked);
	}
	
	function SetToOnlyTextMode(){
		var display="none";
		if(document.getElementById("no_illust").checked){
			display="block";
		}
		document.getElementById("no_illust_alert").style.display=display;
	}
	