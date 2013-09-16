var loader_gif = '<div style="text-align:center; vertical-align: middle;"><img src="/static/img/loader.gif" /></div>'

function load_modal(page) {
    if (page.dbk === ""){var datastring = "";}
    else {var datastring = "k=" + page.dbk;}
    $("#modal_content").html(loader_gif);
    $.ajax({
        url: page.url,
        data: datastring,
        dataType: "html",
        error: function() { $("#modal_content").html('Load Failed :(')},
        success: (function (data) {
            $("#modal_content").html(data);
        })
    });
}


$(document).ready(function () {



    $(".expander").click(function (event){
        if ($(this).hasClass("icon-plus")){
                $("#filter").show();
                $(this).toggleClass("icon-plus", false);
                $(this).toggleClass("icon-minus", true)
            }
        else {
                $("#filter").hide();
                $(this).toggleClass("icon-minus", false);
                $(this).toggleClass("icon-plus", true);
            }
    });


    $("body").on("click", ".modal_view", function (event) {
        var dbk = $(this).data('dbk');
        var url =$(this).data('url')
        var page = {'dbk':dbk, 'url':url}
        load_modal(page);
    });

    
    $("#content_view").on("click", ".show_more", function (event) {
        var url_request = $(this).data('query');
        var content_body = $("#" + $(this).data('parent'));
        $(this).hide();
            $(".eb").html(loader_gif)
        $.ajax({
            url: url_request,
            dataType: "html",
            error: function() { content_body.append('request failed :(');},
            success: (function (data) {
                $(".eb").html("").removeClass("eb")
                content_body.append(data);
            })
        });
    });
    
    $("#modal_content").on("click", ".delete", function (event) {
        var d = 'l=' + encodeURIComponent($(this).data('l')) +"&csrfmiddlewaretoken=" + $("#csrf").val();
        var ar = $('#ar_'+ $(this).data('k'));
        if (window.confirm("Are you sure you want to delete this record?")) {
            $.ajax({
                url: '/edit/resource/delete',
                method: "POST",
                data: d,
                dataType: "html",
                error: function() {alert('fail :(')},
                success: (function (data) {
                    if (data=='deleted'){ 
                        $("#modal_content").modal('hide');
                        ar.hide();
                        }
                    else {alert(data);}
                    
                })
            });
        }
    });

      
    $("#modal_content").on("click", "#save_btn", function () {  
        $.ajax({
               type: "POST",
               url: "/edit/resource/",
               data: $("#popup_form").serialize(), // serializes the form's elements.
               error: function () {$("#save_status").html("error! :(")},
               success: function(data){
                   var d = jQuery.parseJSON(data);
                   $("#save_status").html(d['save_status'])
                   $("#"+d['id']).html(d['ajax_html'])
               }
               
             });
    });
    

    $("#postit").on("click", ".save", function () {
        var close = $(this).hasClass('closetab');
        $.ajax({
               type: "POST",
               url: "/add_new",
               data: $("#postit").serialize(), // serializes the form's elements.
               error: function () {alert('there was an error :(')},
               success: function(data){
                   if (close) {window.close()}
                   else {window.location = data}
               }          
             });
    });


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


     if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
         var pt = true
    }
    else {
        if ($(window).width() > 760 && ($('#sidebar').length)){
                $(window).scroll(function() {
                    if ($(window).width() > 760) {
                        var scrollposition = $(window).scrollTop();
                        var sidebar_parent_offset = $("#content_view").offset().top;
                        var sidebar = $("#sidebar");
                        if (scrollposition > sidebar_parent_offset - 50) {  
                        var top_offset = scrollposition + 50;
                        var sbar_width = $("#sidebar").width();
                        sidebar.css({position: "absolute", width: sbar_width}).offset({top: top_offset});
                        }
                        else {
                        sidebar.css({position: ""}); 
                        }
                    }
                    
                });
        };
        
            $("body").on("mouseenter", ".feed_item", function (event) {
                var ref = $(this).attr('id').replace("ar_", "");
                $("#article_tools_" +ref).show();
                }).on("mouseleave", ".feed_item", function (event) {
                 var ref = $(this).attr('id').replace("ar_", "");
                $("#article_tools_" +ref).hide();
        });
        
        
    }
    
    $(window).resize(function() {
        if ($(window).width() < 760) {
            $("#sidebar").css({position: "static", width: "auto"});
            }
        else {
            var max_width = $("#sidebar_zone").width()
            $("#sidebar").css({width: max_width - 20});
        }
    });
$("#esil").tablesorter();

    function getAllTopicComments(comment_id) {
        var comments = "";

        $.ajax({
            method: 'GET',
            url: '/esil/' + comment_id  + '/comments',
            error: (function () { comments = 'error' }),
            success: (function (data) {
                comments = data;
            })
        });
        return comments;
    }

    function scroll_to_me(JqueryElement) {
        var centerdPoint = ( JqueryElement.offset().top - (window.innerHeight / 2) );
        var scrolltopoint = 0;
        if (window.innerHeight < $(document).height()) {
            if (centerdPoint > 0) { scrolltopoint = centerdPoint }
            $('html, body').animate({
                scrollTop: scrolltopoint
            }, 1000);
        }
    };

    $('body').on("click", ".post_comment", function (event) {

        var reply_to = $(this).data('reply_to');
        var commentID = '#nc' + reply_to;

        $("#id_comment").val($(commentID).val());
        $("#id_reply_to").val(reply_to);

        if (!/^\s*$/.test($("#id_comment").val())) {
            $.ajax({
                method: 'POST',
                url: '/comments/post/',
                data: $('#comment_form').serialize(),
                success: (function (data) {

                    $("#comment_list").html(data);
                    var focuscomment = $( $('.comment' + reply_to)[ ($('.comment' + reply_to).length - 1) ] );
                    scroll_to_me(focuscomment);

                })
            });
        }
    });

    $('body').on("click", ".btn-delete-comment", function (event) {
        var commentID = $(this).data('delete_target');
        if (window.confirm("Are you sure you want to delete this comment?")) {

            $.ajax({
                method: 'GET',
                url: '/esil/comment/delete/' + commentID,
                success: (function (data) {
                    $("#comment_list").html(data);
                })
            });
        }
    });

    $('body').on("click", ".btn-reply-thread", function (event) {
       if ($(this).hasClass('disabled')) {
           $( $(this).data('hide_target') ).hide();
           $(this).removeClass('disabled');
       }
       else {
           $('.disabled.btn-reply-thread').removeClass('disabled')
           $('.comment_mini_form').hide();

           $(this).addClass('disabled');
           $( $(this).data('hide_target') ).show();
           $( $(this).data('textarea_target') ).select();
       }

    });



 });
