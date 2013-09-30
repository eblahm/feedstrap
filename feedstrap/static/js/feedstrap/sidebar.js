

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

});
