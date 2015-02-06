$(document).ready( function() {
    "use strict";
    $('#api_form').submit(function(event) {
        var url = window.location.protocol + '//' + window.location.host + '/game_api/v1/' + $('#query').val();
        $.getJSON(url).done(function(data) {
            $('#query_result').html(JSON.stringify(data, undefined, 2));
        }).fail(function(data) {
            $('#query_result').html('Oops, something went wrong, check your query (make sure you are logged in as a developer to access /sales/).');
        });
        event.preventDefault();
    });
});