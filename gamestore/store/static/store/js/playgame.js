$(document).ready( function() {
    "use strict";
    
    window.addEventListener("message", function(event) {
        if (event.origin !== "{{ gameurl }}") //how to do this when script is placed in a static file, just go with '*' ?
            return;
        
        if (event.data.messageType === "SAVE") {
            //save the gamestate
            $.ajax({
                "url" : "../save",
                "type" : "POST",
                "data" : {"gamestate" : JSON.stringify(event.data.gameState)}
            });
        }
        else if (event.data.messageType === "LOAD_REQUEST") {
            //load a gamestate and send it back via postMessage
            $.getJSON("../save", function(data) {
                $("#gameframe").get(0).postMessage({
                   "messageType" : "LOAD",
                    "gameState" : data.gameState //do we need to JSON.parse() ?
                });
            });
        }
        else if (event.data.messageType === "SCORE") {
            //save a score
            $.ajax({
                "url" : "../scores",
                "type" : "POST",
                "data" : {"score" : JSON.stringify(event.data.score)}
            });
        }
    }, false);
});