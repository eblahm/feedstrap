$(document).ready(function () {

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

});
