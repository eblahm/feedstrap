var loader_gif = '<div style="text-align:center; vertical-align: middle;"><img src="/feedstrap/static/img/loader.gif" /></div>'
function load_modal(db_key, url_string="/db/edit/resource") {
    var datastring = "k=" + db_key;
    $("#modal_content").html(loader_gif);
    $.ajax({
        url: url_string,
        data: datastring,
        dataType: "html",
        error: function() { $("#modal_content").html('Load Failed :(')},
        success: (function (data) {

            $("#modal_content").html(data);
        })
    });
}



$(document).ready(function () {

    $("#content_box").on("click", ".db_view", function (event) {
        var db_key = $(this).data('dbk');
        load_modal(db_key);
    });

//    $("#content_box").on("click", ".read", function (event) {
//        var db_key = $(this).data('dbk');
//        load_modal(db_key, url_string="/db/read");
//    });
    
    $("#content_box").on("click", ".show_more", function (event) {
        var url_request = $(this).data('query');
        var content_body = $("#content_view");
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
               url: "/db/edit/resource/",
               data: $("#popup_form").serialize(), // serializes the form's elements.
               error: function () {$("#save_status").html("error! :(")},
               success: function(data){
                   var d = jQuery.parseJSON(data);
                   $("#save_status").html(d['save_status'])
                   $("#"+d['id']).html(d['ajax_html'])
               }
               
             });
    });


    $("#content_box").on("mouseenter", ".feed_item", function (event) {
        var ref = $(this).attr('id').replace("ar_", "");
        $("#article_tools_" +ref).show();
        }).on("mouseleave", ".feed_item", function (event) {
         var ref = $(this).attr('id').replace("ar_", "");
        $("#article_tools_" +ref).hide();
});


});
