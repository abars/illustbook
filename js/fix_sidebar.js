//サイドバーを固定する

$(function(){
	var margin_top_px=4;
	var margin_bottom_px=32;
	var contentHeight = $("html, body").height();

	var windowWidth=$(this).width();
	var windowHeight = $(window).height();

	var side = $("#side");
	var sideHeight = side.outerHeight() + margin_bottom_px;
	var sidePositionLeft = side.position().left;
	var sidePositionTop = side.position().top;

	function on_scroll(){
		var scrollTop = $(this).scrollTop();

		var visibleBottom = scrollTop + windowHeight;	//有効視界領域の一番下のピクセル数
		var sideBottom = sidePositionTop + sideHeight;	//サイドバーを通常配置した場合の一番下のピクセル数

		var footerBottom = $("#contents-footer").position().top;	//フッターまで来たらフッターを一番下のピクセルとする
		if(visibleBottom>footerBottom){
			visibleBottom=footerBottom;
		}

		if(sideHeight<windowHeight){
			if(sidePositionTop<scrollTop+margin_top_px){
				side.css({position:"fixed", left:sidePositionLeft, top: margin_top_px});
			} else {
				side.css({position:"static", left: "auto", bottom: "auto"});
			}
		 }else{
		 	if(sideBottom<=visibleBottom){
				side.css({position:"fixed", left:sidePositionLeft, top: visibleBottom-scrollTop-sideHeight});
			} else {
				side.css({position:"static", left: "auto", bottom: "auto"});
			}
		 }
	}

	$(window).resize(function(){
		windowHeight = $(this).height();
		if(windowWidth!=$(this).width()){
			windowWidth=$(this).width();
			side.css({position:"static", left: "auto", bottom: "auto"});
			sidePositionLeft = side.position().left;
			sidePositionTop = side.position().top;
			on_scroll();
		}
	});

	$(window).scroll(on_scroll);
});
