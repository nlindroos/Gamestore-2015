$(document).ready( function() {
    "use strict";
    
    //csrf related stuff from djangodocs:
    /////////////////////////////////////
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    /////////////////////////////////////
    
    //ok, now this is the relevant part:
    window.addEventListener("message", function(event) {
        if ($("#gameframe").attr('src').indexOf(event.origin) !== 0)
            return;
        
        if (event.data.messageType === "SAVE") {
            //save the gamestate
            $.ajax({
                "url" : window.location.href + "/save",
                "type" : "POST",
                "data" : {
                    "gamestate" : JSON.stringify(event.data.gameState)
                }
            }).done(function() {
                $("#gameframe").get(0).contentWindow.postMessage({
                   "messageType" : "MESSAGE",
                    "message" : "Game state saved succesfully!"
                }, event.origin);
            }).fail(function() {
                $("#gameframe").get(0).contentWindow.postMessage({
                   "messageType" : "MESSAGE",
                    "message" : "Saving game state failed."
                }, event.origin);
            });
        }
        else if (event.data.messageType === "LOAD_REQUEST") {
            //load a gamestate and send it back via postMessage
            $.getJSON(window.location.href + "/save", function(data) {
                $("#gameframe").get(0).contentWindow.postMessage({
                   "messageType" : "LOAD",
                    "gameState" : data //this data is just the gamestate, see views.py
                }, event.origin);
            }).done(function() {
                $("#gameframe").get(0).contentWindow.postMessage({
                   "messageType" : "MESSAGE",
                    "message" : "Game state loaded succesfully!"
                }, event.origin);
            }).fail(function() {
                $("#gameframe").get(0).contentWindow.postMessage({
                   "messageType" : "MESSAGE",
                    "message" : "Loading game state failed."
                }, event.origin);
            });;
        }
        else if (event.data.messageType === "SCORE") {
            //save a score
            $.ajax({
                "url" : window.location.href + "/scores",
                "type" : "POST",
                "data" : {
                    "score" : JSON.stringify(event.data.score)
                }
            }).done(function() {
                $("#gameframe").get(0).contentWindow.postMessage({
                   "messageType" : "MESSAGE",
                    "message" : "Game score saved succesfully!"
                }, event.origin);
            }).fail(function() {
                $("#gameframe").get(0).contentWindow.postMessage({
                   "messageType" : "MESSAGE",
                    "message" : "Saving game score failed."
                }, event.origin);
            });
        }
    }, false);
});