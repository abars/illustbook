//アプリメインクラス
function MyApp(){
	//メンバ変数
	this._canvas=null;
}

//illustbook.app.regist直後に呼ばれる
MyApp.prototype.init=function(){
	//描画領域を確保
	this._canvas=new illustbook.canvas(this,480,480);
	
	//コールバックの登録
	this._canvas.addTouchCallback(this);            //addTouch*が呼ばれるようになる
	illustbook.app.addLoopCallback(this,1000/15);	//loopが呼ばれるようになる
};


//ゲームループ
MyApp.prototype.loop=function(){
    this._canvas.drawBegin();
    this._canvas.fillRect(0,0,this._canvas.width,this._canvas.height,0xeeeeee);
    this._canvas.drawText("Hello World",0,20,12,0x000000);
    this._canvas.drawEnd();
};

//タッチされたか、マウスでクリックされた
MyApp.prototype.onTouchStart=function(x,y){
};

//タッチしながら移動されたか、マウスが移動した(ドラッグ中で無くても呼ばれる)
MyApp.prototype.onTouchMove=function(x,y){
};

//タッチが終了されたか、マウスを離した
MyApp.prototype.onTouchEnd=function(){
};

//イラストブックにアプリを登録する
illustbook.app.regist(new MyApp());
