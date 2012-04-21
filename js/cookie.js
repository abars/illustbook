//--------------------------------------------------------
//お絵かきツールのCookie
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

	function loadCookie(){
		var data=new Object();
		if(document.cookie){
			var cookies = document.cookie.split("; ");
			for (var i = 0; i < cookies.length; i++) {
				var str = cookies[i].split("=");
				var cookie_value = unescape(str[1]);
				data[str[0]]=cookie_value;
			}
		}
		if(data["name"])
			document.getElementById("name").value=data["name"];
		if(data["adr"] && document.getElementById("homepage_addr"))
			document.getElementById("homepage_addr").value=data["adr"];
	}
