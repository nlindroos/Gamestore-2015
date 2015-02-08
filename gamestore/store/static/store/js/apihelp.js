$(document).ready( function() {
    "use strict";
    $('#api_form').submit(function(event) {
        var url = window.location.protocol + '//' + window.location.host + '/game_api/v1/' + $('#query').val();
        $.getJSON(url).done(function(data) {
            $('#query_result').html(JSON.stringify(data, undefined, 2));
        }).fail(function(jqXHR, text, error) {
            if (jqXHR.status == 404 || jqXHR.status == 403) {
                $('#query_result').html(jqXHR.status + ': ' + error);
            }
            else {
                $('#query_result').html('Oops, something went wrong. Make sure you are logged in.');
            }
        });
        event.preventDefault();
    });
});