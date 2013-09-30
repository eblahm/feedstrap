

require(["static/js/feedstrap/utils"], function(utils) {
    $(document).ready(function () {

        $("#esil").tablesorter();

        $(".topic_row").on({

          click: function() {
            var loc = '/esil/' + $(this).data('k') + '/';
            window.location.href=loc;
          }
        });

          $(".show_des").click(function (event){
            event.stopPropagation();
            var parent = $(this).data('parent');
            var full = $(this).data('full');
            $("#" + parent).html(full);

         });

    });

});
