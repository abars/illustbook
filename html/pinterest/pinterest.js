<script>

{% if illust_enable %}
$(function(){
	
var $container = $('#container');	
	
  function masonry_exec(){
      $container.masonry({
        itemSelector: '.item',
        isFitWidth: true
      });
    $('#index').width($container.width())
  }

masonry_exec();

$( window ).resize(function(){
  masonry_exec();
});

	$container.infinitescroll({
      navSelector  : '#page-nav',    // selector for the paged navigation 
      nextSelector : '#page-nav a',  // selector for the NEXT link (to page 2)
      itemSelector : '.item',     // selector for all items you'll retrieve
      loading: {
          finishedMsg: '<div style="background-color:#ffffff;z-index:2;">ページの終端です。</div>',
          img: 'static_files/loading.gif',
          msgText: '<div style="background-color:#ffffff;z-index:2;">次のページを読込中</div>'
        }
      },
      // trigger Masonry as a callback
      function( newElements ) {
        var $newElems = $( newElements );
        $container.masonry( 'appended', $newElems, true ); 
      }
    );
});
{% endif %}

function show_more_tag(){
  if($('#more_tag').is(':visible')){
   $('#more_tag').hide();
   $('#show_more_tag_button').show();
  }else{
   $('#more_tag').show();
   $('#show_more_tag_button').hide();
  }
}

function show_follower(){
  if($('#follower').is(':visible')){
    $('#follower').hide();
    $('#follower_button').show();  
  }else{
    $('#follower').show();
    $('#follower_button').hide();  
  }
}

function show_profile(){
  if($('#profile').is(':visible')){
    $('#profile').hide();
    $('#profile_button').text("詳細")
  }else{
   $('#profile').show();  
    $('#profile_button').text("閉じる")
  }
}
</script>
