<script>

{% if illust_enable %}
$(function(){
	
var $container = $('#container');	
	
  $container.imagesLoaded(function(){
      $container.masonry({
        itemSelector: '.item',
      });
    });

	$container.infinitescroll({
      navSelector  : '#page-nav',    // selector for the paged navigation 
      nextSelector : '#page-nav a',  // selector for the NEXT link (to page 2)
      itemSelector : '.item',     // selector for all items you'll retrieve
      loading: {
          finishedMsg: '<div style="background-color:#ffffff;">ページの終端です。</div>',
          img: 'static_files/loading.gif',
          msgText: '<div style="background-color:#ffffff;">次のページを読込中</div>'
        }
      },
      // trigger Masonry as a callback
      function( newElements ) {
        // hide new items while they are loading
        var $newElems = $( newElements ).css({ opacity: 0 });
        // ensure that images load before adding to masonry layout
        $newElems.imagesLoaded(function(){
          // show elems now they're ready
          $newElems.animate({ opacity: 1 });
          $container.masonry( 'appended', $newElems, true ); 
        });
      }
    );
});
{% endif %}

function show_more_tag(){
  $('#more_tag').show();
  $('#show_more_tag_button').hide();
}
</script>
