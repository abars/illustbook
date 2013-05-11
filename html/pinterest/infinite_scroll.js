<script type="text/javascript">
/* for w3c validater */
/* <![CDATA[ */

  function set_return_to_top(){
    $(function () {
        $(window).scroll(function () {
            if ($(this).scrollTop() > 100) {
                $('#back-top').fadeIn();
            } else {
                $('#back-top').stop().fadeOut();
            }
        });
        // scroll body to 0px on click
        $('#back-top a').click(function () {
            $('body,html').animate({
                scrollTop: 0
            }, 800);
            return false;
        });
    });    
  }

$(document).ready(function(){
  set_return_to_top();
});

$(function(){
	var $container = $('#infinite-scroll-container');

	$container.infinitescroll({
      navSelector  : '#page-nav',    // selector for the paged navigation 
      nextSelector : '#page-nav a',  // selector for the NEXT link (to page 2)
      itemSelector : '{{infinite_scroll_selecter}}',     // selector for all items you'll retrieve
      bufferPx : 2000, // 最も下に行く前にロードをかける
      loading: {
          finishedMsg: '<div class="loading">ページの終端です。</div>',
          img: '{{host}}static_files/loading.gif',
          msgText: '<div class="loading">次のページを読込中</div>'
        }
      },
      // trigger Masonry as a callback
      function( newElements ) {
        {% if use_masonry %}
          var $newElems = $( newElements );
          $newElems.css({ opacity: 0 });
          $container.masonry( 'appended', $newElems, true ); 
          $newElems.animate({ opacity: 1 });
        {% endif %}
      }
    );
});

/* ]]> */
</script>
