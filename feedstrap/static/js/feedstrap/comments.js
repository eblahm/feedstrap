

$(document).ready(function () {

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
        var subscribeID = '#subscribe' + reply_to;

        $("#id_comment").val($(commentID).val());

        $("#id_followup").prop('checked', $(subscribeID).prop('checked'));
        $("#id_reply_to").val(reply_to);

        if (!/^\s*$/.test($("#id_comment").val())) {
            $.ajax({
                method: 'POST',
                url: '/esil/comments/post/',
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
