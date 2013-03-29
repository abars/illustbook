	//================================================
    //WacomTabletPlugin(ver2)を使用する
	//================================================

	var WACOM_PLUGIN_CHECK_INTERVAL=1000;

	var m_wacom_plugin=null;
	var m_plugin_load_finish=false;
	var m_abort_count=0;
	var m_plugin_version="0.0.0.0";
	
	//================================================
	//プラグインの読み込み
	//================================================

	//まずプラグインを読み込みに行く
	function initWacom(){
		//プラグインを有効化
		var text="<!--[if IE]><object width='1px' height='1px' id='Wacom' classid='CLSID:092dfa86-5807-5a94-bf3b-5a53ba9e5308' codebase='fbWacomTabletPlugin.cab'></object><![endif]--><!--[if !IE]> <--><!-- This is the Firebreath wacomtabletplugin --><object width='1px' height='1px' id='Wacom' type='application/x-wacomtabletplugin'></object><!--><![endif]-->";
		document.getElementById("wacomPlugin").innerHTML=text;
		checkWacom();
	}
	
	//プラグインを取得
	function checkWacom(){
		//Pluginを取得
		m_wacom_plugin=document.getElementById('Wacom');
		
		//プラグインが存在すれば読み込み完了
		if(m_wacom_plugin && m_wacom_plugin.penAPI){
			m_plugin_version=m_wacom_plugin.version;
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
		m_wacom_plugin=null;
		m_plugin_load_finish=true;
	}

	//プラグインの読み込みが完了
	function isPluginLoadFinish(){
		return m_plugin_load_finish;
	}
	
	//================================================
	//互換性用
	//================================================

	//最新版は筆圧が取得できる
	function isSupportBrowser(){
		return checkIsRatestPlugin();
	}
	
	//サポートしていなかった場合にFlash上に表示されるメッセージを取得する
	var m_notify_text="";

	function getNotifyText(){
		return m_notify_text;
	}
	
	function getWacomPluginVersion(){
		var obj=new Object();
		var ver=m_plugin_version.split(".");
		if(ver.length!=4){
			return null;
		}
		obj.major=Number(ver[0]);
		obj.minur1=Number(ver[1]);
		obj.minur2=Number(ver[2]);
		obj.minur3=Number(ver[3]);
		return obj;
	}
	
	function checkIsRatestPlugin(){
		var obj=getWacomPluginVersion();
		if(m_wacom_plugin==null || obj==null){
			m_notify_text="筆圧を使用するにはWacomの最新のドライバをインストールして下さい。";
			return false;
		}
		
		//alert("ver"+obj.major+"."+obj.minur1+"."+obj.minur2+"."+obj.minur3);
		
		if(obj.major<2 || obj.minur1<1 || obj.minur2<0 || obj.minur3<2){
			m_notify_text="Wacomのドライバを更新すると筆圧を使用できます。　";
			m_notify_text+="現在："+obj.major+"."+obj.minur1+"."+obj.minur2+"."+obj.minur3+"　";
			m_notify_text+="要求：2.1.0.2以降\n";
			return false;
		}
		
		return true;
	}

	//================================================
	//筆圧の取得
	//================================================
	
	function getPressure(){
		if(!isPen()){
			return 0.5;
		}
		return m_wacom_plugin.pressure;
	}
	
	function isPen(){
		if(!m_wacom_plugin){
			return false;
		}
		var pointer_type=m_wacom_plugin.pointerType;
		if(pointer_type==1 || pointer_type==3){	// 1==Pen 3==Eraser
			return true;
		}
		return false;
	}
	
	function isEraser(){
		if(!m_wacom_plugin){
			return 0;
		}
		return m_wacom_plugin.isEraser;
	}
