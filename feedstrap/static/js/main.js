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
var sbar_loadstate = $("#sidebar").width();

$(window).scroll(function() {
    var scrollposition = $(window).scrollTop();
    var sidebar_parent_offset = $("#content_view").offset().top;
    var sidebar = $("#sidebar");
    if (scrollposition > sidebar_parent_offset - 50) {  
    var top_offset = scrollposition + 50;
    sidebar.css({position: "absolute", width: sbar_loadstate}).offset({top: top_offset});
    }
    else {
    sidebar.css({position: ""}); 
    }
    
});


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

//    $("#content_view").on("click", ".read", function (event) {
//        var db_key = $(this).data('dbk');
//        load_modal(db_key, url_string="/read");
//    });
    
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
    
    $("body").on("mouseenter", ".feed_item", function (event) {
        var ref = $(this).attr('id').replace("ar_", "");
        $("#article_tools_" +ref).show();
        }).on("mouseleave", ".feed_item", function (event) {
         var ref = $(this).attr('id').replace("ar_", "");
        $("#article_tools_" +ref).hide();
});

    $(".topic_row").on({
    
      click: function() {
        var k = $(this).data('k'); 
        window.location.href='/esil?k='+k;
      }
    });
    
      $(".show_des").click(function (event){
        event.stopPropagation();
        var parent = $(this).data('parent');
        var full = $(this).data('full');
        $("#" + parent).html(full);
     
     });

});
