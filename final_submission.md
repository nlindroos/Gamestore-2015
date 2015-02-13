# Gamestore API

Gamestore 2015 offers a free public API for anyone to use.
The API can be used to get information about the games, their sales, highscores and more.
The API uses a simple REST interface and returns results as JSON.

## Table of Contents

*   [Requests](#requests)

    *   [Game Requests](#game_requests)
    *   [Sales Requests](#sales_requests)
*   [Responses](#responses)
    *   [JSONP](#jsonp)

## Requests

Queries to the API are made using HTTP GET requests. 
There are two types of requests: game requests and sales requests (the latter is for developers only). 

### Game Requests

    `/game_api/v1/games/`

The URL above will return all games. The result set can be limited by game title, id, developer name or by tags.

    `/game_api/v1/games/id/5`

    `/game_api/v1/games/title/some_title`

    `/game_api/v1/games/dev/some_developer`

    `/game_api/v1/games/tagged/some_tag`

Titles and developer names may contain spaces. Instead of spaces, use plus signs (+) in the URL:

    `/game_api/v1/games/title/my+awesome+game`

Titles may contain special characters. In searches, one should simply omit all non-alphanumeric, non-underscore characters,
    except the percent sign (%) and the ampersand (&amp;), which should be replaced by the words 'percent' and 'and' respectively.

For example, the following URL finds games titled 'Crash & burn' (but also 'Crash and burn'):

    `/game_api/v1/games/title/crash+and+burn`

Unicode letters should be percent escaped in the URL (note that browsers may do this automatically).

For example, the following URL will find games with titles ending with the letter ö:

    `/game_api/v1/games/title/*%C3%B6`

Alternatively, wildcards may also be used in all of the situations mentioned above.

#### Wildcards

The asterisk (*) may be used as a wildcard for titles, developer names or tags (matching any number of unknown characters). 
For example, the following URL will get all games developed by any developer whose name ends with
'studios':

    `/game_api/v1/games/dev/*studios`

Similarly, this URL will get all games whose title contains the word 'awesome':

    `/game_api/v1/games/dev/*awesome*`

#### Multiple filters

It is also possible to limit games by sets of IDs, titles, developers and tags.
This is done simply by appending another filter. For example, the following URL will
find both of the games 'My Little Ostrich Farm' and 'Bird Farming Deluxe':

    `/game_api/v1/games/title/my+little+ostrich+farm/title/bird+farming+deluxe`

Chaining IDs, titles and developers in the way presented above returns games that match any of the filters.
When filtering by tags, it is possible to choose whether the result should include games 
matching any of the tag filters, or only games that match all of them:

    `/game_api/v1/games/tagged/puzzle/tagged/adventure?tagfilter=any`

    `/game_api/v1/games/tagged/puzzle/tagged/adventure?tagfilter=all`

Filters for titles, developers and tags (but not IDs) can also be mixed.
The following URL gets all games whose title begins with the letter 'a', developed by
a developer called 'FTW Studios' and tagged 'puzzle':

    `/game_api/v1/games/title/a*/dev/ftw+studios/tagged/puzzle`

When mixing filters, they must be in the order title, developer, tag.
For example, the following works:

    `/game_api/v1/games/title/castle*/title/tower*/dev/*games/tagged/puzzle/tagged/survival`

Whereas the following does not work:

    `/game_api/v1/games/title/castle*/tagged/puzzle/title/tower*/tagged/survival/dev/*games`

#### Expanding Responses

Game request responses can be expanded with additional content using the 'expand' query string option:

*   highscores (shows top N highscores for each game):  `game_api/v1/games/?expand=highscores(10)`
*   similars (shows top N most similar games for each game): `game_api/v1/games/?expand=similars(10)`

Multiple expand options can be given at the same time, using commas (,) as separator:

    `game_api/v1/games/?expand=highscores(10),similars(3)`

### Sales Requests

Developers can use this part of the API to check details about their sales.

In order to access this part of the API, you must be logged in as a developer.

    `/game_api/v1/sales/`

The URL above will get all sales of the developer currently logged in

The result set can be limited by either game IDs or game titles. This is done the same way as for game requests
    ([see above](#game_requests)), except that `gameid` should be used instead of `id`.

    `/game_api/v1/sales/gameid/4`

    `/game_api/v1/sales/title/shoe+lace+simulator+2000`

#### Filtering by date

Sales requests can be filtered by date as well as by games:

    `/game_api/v1/sales/startdate/2015-01-01/`

    `/game_api/v1/sales/enddate/2015-08-01/`

    `/game_api/v1/sales/startdate/2015-01-01/enddate/2015-08-01/`

## Responses

The response of GET requests is a JSON object. Rather than giving specifics about what these objects look like,
we provide you with an interactive way to figure it out yourself ([see below](#try_it)).

### JSONP

The JSON response can be wrapped in a callback function (to get JSONP) using the 'callback' querystring option.
For example:

    `game_api/v1/games/?callback=mycallback`

    