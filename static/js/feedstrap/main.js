



require(["/static/js/feedstrap/utils.js"], function(utils) {
    $(document).ready(function () {

        $("body").on("click", ".modal_view", function (event) {
            var dbk = $(this).data('dbk');
            var url =$(this).data('url')
            var page = {'dbk':dbk, 'url':url}
            load_modal(page);
        });

        $('#modal_content').on('shown', function () {
            $('#description').focus();
        })


        $("#modal_content").on("click", ".delete", function (event) {
            var d = 'l=' + encodeURIComponent($(this).data('l')) +"&csrfmiddlewaretoken=" + $("#csrf").val();
            var ar = $('#ar_'+ $(this).data('k'));
            if (window.confirm("Are you sure you want to delete this record?")) {
                $.ajax({
                    url: '/edit/resource/delete',
                    method: "POST",
                    data: d,
                    dataType: "html",
                    error: (function() {alert('fail :(')} ),
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

    });

});
