$(document).ready(function() {
    "use strict";
    $("#find_my_score").click(function() {
        $('html, body').animate({
            scrollTop: $("#my_score").offset().top
        }, 1500);
    });
});