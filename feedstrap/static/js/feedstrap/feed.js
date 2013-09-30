



require(["static/js/feedstrap/utils"], function(utils) {
    $(document).ready(function () {

        // when the mouse hovers over a feed item, show the edit button
        // when the mouse leaves, hide the edit button
        $("body")
            .on("mouseenter", ".feed_item", function (event) {
                var ref = $(this).attr('id').replace("ar_", "");
                $("#article_tools_" +ref).show();
            })
            .on("mouseleave", ".feed_item", function (event) {
                var ref = $(this).attr('id').replace("ar_", "");
                $("#article_tools_" +ref).hide();
            });

        // load more feed items when the user clicks the "show more" button
        $("#content_view")
            .on("click", ".show_more", function (event) {

                var url_request = $(this).data('query');
                var content_body = $("#" + $(this).data('parent'));

                $(this).hide();
                $(".eb").html(loader_gif);

                $.ajax({
                    url: url_request,
                    dataType: "html",
                    error: (function() { content_body.append('request failed :(');}),
                    success: (function (data) {

                        $(".eb").html("").removeClass("eb");
                        content_body.append(data);

                    })
                });

            });

    });
});
