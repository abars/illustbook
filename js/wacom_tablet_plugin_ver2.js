	//================================================
    //WacomTabletPlugin(ver2)を使用する
	//================================================

	var WACOM_PLUGIN_CHECK_INTERVAL=1000;

	var m_wacom_plugin=null;
	var m_plugin_load_finish=false;
	var m_abort_count=0;
	
	//================================================
	//プラグインの読み込み
	//================================================

	//まずプラグインを読み込みに行く
	function initWacom(){
		//プラグインを有効化
		var text="<!--[if IE]><object id='Wacom' classid='CLSID:092dfa86-5807-5a94-bf3b-5a53ba9e5308' codebase='fbWacomTabletPlugin.cab'></object><![endif]--><!--[if !IE]> <--><!-- This is the Firebreath wacomtabletplugin --><object id='Wacom' type='application/x-wacomtabletplugin'></object><!--><![endif]-->";
		document.getElementById("wacomPlugin").innerHTML=text;
		checkWacom();
	}
	
	//プラグインを取得
	function checkWacom(){
		//Pluginを取得
		m_wacom_plugin=document.getElementById('Wacom');
		
		//プラグインが存在すれば読み込み完了
		if(m_wacom_plugin && m_wacom_plugin.penAPI){
			m_wacom_plugin=m_wacom_plugin.penAPI;
			m_plugin_load_finish=true;
			return;
		}
		
		//プラグインが存在しない場合はもう一度探しに行く
		m_abort_count++;
		if(m_abort_count<5){
			setTimeout("checkWacom()",WACOM_PLUGIN_CHECK_INTERVAL);
			return;
		}

		//プラグインのインストールを要求する
		requestPluginInstall();
	}

	//プラグインのインストールを要求する
	function requestPluginInstall(){
		var txt="<A HREF='http://www.wacom.com/CustomerCare/Plugin.aspx' TARGET='_BLANK'>WacomTabletDataPlugin</A>のUpdateで全てのブラウザで筆圧が使用できるようになりました。<BR>";
		txt+="次のリンクからプラグインをインストールして下さい。　<A HREF='http://www.wacomeng.com/web/fbWTPInstall.zip' TARGET='_BLANK'>Windows用</A>　<A HREF='http://www.wacomeng.com/web/Wacom%20Mac%20Plug-in%20Installer.zip' TARGET='_BLANK'>Mac用</A>　<A HREF='javascript:requestFinish();'>今回はインストールしない</A><BR>";
		get_flex_object().height="90%";
		document.getElementById("wacomPlugin").innerHTML=txt;
	}
	
	function requestFinish(){
		get_flex_object().height="100%";
		document.getElementById("wacomPlugin").innerHTML="";
	}
	
	function isPluginLoadFinish(){
		return m_plugin_load_finish;
	}
	
	//================================================
	//互換性用
	//================================================

	//ver2になって必ず筆圧は取得できるようになった
	function isSupportBrowser(){
		return true;
	}
	
	//サポートしていなかった場合にFlash上に表示されるメッセージを取得する
	function getNotifyText(){
		return "";
	}

	//================================================
	//筆圧の取得
	//================================================
	
	function getPressure(){
		if(!isPen())
			return 0.5;
		return m_wacom_plugin.pressure;
	}
	
	function isPen(){
		if(!m_wacom_plugin)
			return false;
		var pointer_type=m_wacom_plugin.pointerType;
		if(pointer_type==1 || pointer_type==3)	// 1==Pen 3==Eraser
			return true;
		return false;
	}
	
	function isEraser(){
		if(!m_wacom_plugin)
			return 0;
		return m_wacom_plugin.isEraser;
	}
