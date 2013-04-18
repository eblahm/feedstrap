$(document).ready(function () {

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
 
})