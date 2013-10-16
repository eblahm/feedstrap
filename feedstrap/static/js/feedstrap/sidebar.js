

$(document).ready(function () {

     // is user on a Desktop?
     // and does the dom actually have a sidebar object?
     if(
         !  (/Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent))
         && ($(window).width() > 760)
         && ($('#sidebar').length)
     )
            {
                $(window).scroll(function() {
                    var scrollposition = $(window).scrollTop();
                    var sidebar_parent_offset = $("#content_view").offset().top;
                    var sidebar = $("#sidebar");
                    if (scrollposition > sidebar_parent_offset - 50)
                    {
                        // as the user scrolls the sidebar follows
                        var top_offset = scrollposition + 50;
                        var sbar_width = $("#sidebar").width();
                        sidebar.css({position: "absolute", width: sbar_width}).offset({top: top_offset});
                    }
                    else
                    {
                        // the user is back to the top of the page
                        // sidebar should no longer be position fixed
                        sidebar.css({position: ""});
                    }
                });
            }

    $(window).resize(function() {
        // the sidebar is fixed, so it has to be manually resized when the window is resized to avoid div overlap
        if ($(window).width() < 760)
        {
            $("#sidebar").css({position: "static", width: "auto"});
        }
        else
        {
            var max_width = $("#sidebar_zone").width();
            $("#sidebar").css({width: max_width - 20});
        }
    });

    $('#sidebar')
        .on('mouseenter', '.sidebar_link', function(){
            $($(this).data('x')).show();
        })
        .on('mouseleave', '.sidebar_link', function(){
            $($(this).data('x')).hide();
        })

    $('body').on('click', '.save_link', function(){
        var fstrings = $(this).data('active-params').split('&').sort();
        var pk =  $(this).data('pk');
        var colors = $.parseJSON($('#pin_mustache').data('colors'));
        var data_dump = '';
        for (var i = 0; i < fstrings.length; i++) {
            var name_value = fstrings[i].split('=')
            if (name_value[0].split('_').length > 1){
                var short_name = name_value[0].split('_')[1];
                var color = colors[short_name];
            }
            else {
                var short_name = name_value[0].split('_')[0];
                var color = colors[short_name];
            }
            if (!(short_name=="")) {short_name=short_name+":"}

            var filter = {
                count:i,
                name:decodeURIComponent(name_value[0]),
                short_name:short_name,
                value:decodeURIComponent(name_value[1]),
                color: color
            }
            data_dump = data_dump + $.mustache($('#pin_mustache').html(), filter);
        }

        $('#filter_tags_modal').html(data_dump);
        if (!(pk==undefined)){
            $('#save_link_form > [name="name"]').val($(this).data('name'));
            $('#filter_tags_modal').append(
                $.mustache('<input style="display: none" name="pk" value="{{pk}}">', {pk:pk})
            );
            $('#delete_link').show();
        }
        else {
            $('#save_link_form > [name="name"]').val('');
            $('#delete_link').hide();
        }
    });

    $('body').on('click', '.xpin', function(){
       $($(this).data('target')).html("")
    });

    $('#save_link_modal').on('click', '#submit_save_link', function(){
        $('form#save_link_form').submit();
    });

    $('#save_link_modal').on('click', '#delete_link', function(){
        $.ajax({
            url: $(this).data('url'),
            method: 'POST',
            data: $('#save_link_form').serialize(),
            error: (function(){ alert('error :(') }),
            success: function() {
                document.location = $('#sl_redirect').val();
            }
        });
        $($(this).data('target')).html("")
    });

});
