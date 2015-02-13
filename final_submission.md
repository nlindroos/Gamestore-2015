
# [Gamestore 2015](http://gamestore2015.herokuapp.com) - Final submission

## Our names and student IDs
Martin Granholm, 217754
Johan Gädda, 84565T
Niklas Lindroos, 218177

## Features we implemented and our point suggestions for those features
### Mandatory requirements
#### Authentication
Our solution enables login, logout and register functionalities for players and developers by using Django auth. The division into players and developers was done using Django’s group system. The email validation system is somewhat crippled, due to the fact that we only used Django’s Console Backend. As an end-user probably can’t see the mail written to the server’s stdout, we added the confirmation link on the registration page as a work-around. All in all, authentication works as required in the project description.
Point suggestion: 200/200

#### Basic player functionalities
Our solution communicates with Niksula’s payment system, verifying purchases by calculating and comparing the given checksums and ref numbers. Added games are completely playable through iframes. Games can be searched using a filter system, which enables filtering based on game title, tags and price. We believe our solution satisfies the requirement for max points.
Point suggestion: 300/300

#### Basic developer functionalities
Developers can add games and manage the attributes of a game, such as title, price and description. Developers can also remove games at will (slightly dangerous feature, but hey it was in the project description). Developers can also see basic statistics of how many times their game has been bought and how much money they’ve made in total. Additional statistics can be accessed through the provided RESTful API.
Point suggestion: 200/200

#### Game/service interaction
After a player has finished playing a game, the score will be submitted to the parent window. The score is also recorded into the highscore tables, provided that this score is an improvement on the player’s previous best score. Messages from the service to the game are sent to notify about the highscore situation after a score has been sent (the message states the score sent to the server and whether the score qualifies for a personal best, world record or neither). Messages are also sent to notify about save/load success/failure.
Point suggestion: 200/200

#### Quality of work
We estimate that the quality of the code and commenting is generally on a satisfactory level. We have also succeeded fairly well in utilizing Django’s separation of concerns-mindset. The user experience largely follows the standards set by other web-based services. Still, we see that some small improvements could be done here and there to improve quality. Test coverage could be improved and more unit tests added.
Point suggestion: 80/100

### Optional requirements
#### Save/load feature
Our service supports the save/load feature using the given simple message protocol. We feel that this feature fully meets the requirements in the project description.
Point suggestion: 100/100

#### 3rd party login
The third party login was implemented by using the external python-social-auth library. As of now, the service only support Google Oauth, but new methods could easily be added.
Point suggestion: 100/100

#### RESTful API
The service features a relatively extensive and well-documented API, which enables access to data about available games, high scores and sales. More details can be found at: http://gamestore2015.herokuapp.com/game_api/v1/help. The API is somewhat limited in the sense that it only supports GET requests. It also seems to be debatable whether Django’s cookie based authentication is completely in line with the REST philosophy (authentication is needed for the sales section of the API). Nonetheless, we feel that this is one of the highlights of our service and worth full points.
Point suggestion: 100/100

#### Own game
Another highlight of our service is our very own game, ‘Adventure of Save Button’. This exciting game cleverly incorporates the save/load feature into the game experience itself. With respect to the requirements this game is way overkill. Totally worth full points.
Point suggestion: 100/100

#### Mobile friendly
The service was developed with mobile friendliness in mind (using Bootstrap) and the end result is indeed quite mobile friendly. Playing games on mobile is however not the best idea, but this is only due to the fact that there are not (yet :P) any truly mobile friendly games in our service.
Point suggestion: 50/50

#### Social media sharing
Our group members are quite SoMe-averse, so we decided to skip this feature.
Point suggestion: 0/50

#### Non-functional requirements
We feel that the overall level of documentation is fairly good. Our teamwork was quite smooth throughout the project and we made extensive use of many different communication methods. The primary forum of communication regarding features, bugs and to-dos was the Trello board (link: https://trello.com/b/30jjvjap/wsd-project).
We also used Google Drive for documentation purposes and to give a high-level overview of the project’s progress (link: https://drive.google.com/folderview?id=0B8ftVfJ44Xq7T25BS1NqbHJ1MUk&usp=sharing).
For instant messaging, we used Google Hangouts. We used GitLab commenting very rarely, preferring instead to discuss issues on Trello.
Finally, we had a weekly 4-hour slot on Mondays where we worked together on the project (this can be seen as a peak of commits around Monday).
Point suggestion: 200/200

#### Total points suggestion
Our suggestion for the total amount of points: 1630/1700

## Where were we successful and where did we have most problems?
### Successes:
#### API
The interactive API console works neatly. The API is also well documented and tested.
#### Own game (Adventure of Save Button)
A considerable amount of time has been spent making the divs move. As a side effect, the game is playable even on a mobile phone.
#### Overall result
The overall result of the project was quite good in our opinion and the web application doesn’t look too shabby. It would be easy to continue working on the project, adding new features and improving existing ones.
#### Teamwork
Trello worked well as a platform. Our weekly meetings turned out to be useful. Team members notified each other of bugs and helped fix issues together.

### Challenges:
#### Many issues with third-party auth
Adding a third-party solution was challenging due to the minimalistic documentation. A lot of trial-and-error was required to learn how the library actually behaved.
#### Hard to find the best solution for creating two distinct user groups
We debated and googled extensively for the smartest way to separate players and developers from each other. We finally chose to use the built-in user groups instead of e.g. extending the user models. After all, the users had quite similar attributes, they just required different permissions.
#### Testing practices
We had difficulties maintaining the principle of testing a feature before assuming it as “done” and starting on the next feature.
#### Initial difficulties with Heroku deployment
Following Heroku’s own instructions led us astray, but the lecture slides brought us back to the light. We had to delete our application from Heroku several times and redeploy it before it worked.

## The division of work between team members
Our team members had quite varying levels of programming experience. We divided the work according to the members’ previous experience and interest areas. Naturally, we helped each other on almost everything, so the following division is slightly forced:

Martin created the skeleton for the gamestore, working with many of the basic player and developer functionalities. He also implemented the RESTful API and the game “Adventure of Save Button”.

Niklas was our primary UI responsible, as he had previous Bootstrap experience. He created many of the templates and worked with Martin on many of the key player and developer functionalities.

Johan worked with the more decoupled parts of the project, such as user management and the payment system. He was mainly responsible for django auth and third-party authentication as well as administration of project management tools.

## Instructions on how to use the application
[Gamestore 2015](http://gamestore2015.herokuapp.com) is a game service that supports uploading, modifying and playing games. To be able to use these features, the user is required to log in. There are two types of users: developers and players. A developer (belonging to the group Developers) can upload games, edit game attributes and remove his own games. A player (belonging to the group Players) can view details about and highscores of games, view related games, and purchase and, of course, play games.

A user can log in with Google login, a previously created Gamestore 2015 account, or create a completely new account. The Google login can only be used to log in as a player. When a player logs in, he is redirected to the ‘My Games’ page. Clicking a game’s name or picture redirects to a more detailed view where the user can view highscores, games sharing the same tags and more games by the same developer.

Games should implement the postmessage protocol as presented in the project description. Otherwise, gameplay itself is completely dependent on the game being played, as all of the game controls are required to be in the game. In other words, the ‘Play game’ page is nothing but a page with an iframe that listens to messages from the game and sends messages to it. There are currently two playable games: the example game and our own game, the other ‘games’ are purely fillers that make it easier to demonstrate site features.

## Gamestore API

Gamestore 2015 offers a free public API for anyone to use.
The API can be used to get information about the games, their sales, highscores and more.
The API uses a simple REST interface and returns results as JSON.

### Requests

Queries to the API are made using HTTP GET requests. 
There are two types of requests: game requests and sales requests (the latter is for developers only). 

#### Game Requests

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

##### Wildcards

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

##### Expanding Responses

Game request responses can be expanded with additional content using the 'expand' query string option:

*   highscores (shows top N highscores for each game):  `game_api/v1/games/?expand=highscores(10)`
*   similars (shows top N most similar games for each game): `game_api/v1/games/?expand=similars(10)`

Multiple expand options can be given at the same time, using commas (,) as separator:

    `game_api/v1/games/?expand=highscores(10),similars(3)`

#### Sales Requests

Developers can use this part of the API to check details about their sales.

In order to access this part of the API, you must be logged in as a developer.

    `/game_api/v1/sales/`

The URL above will get all sales of the developer currently logged in

The result set can be limited by either game IDs or game titles. This is done the same way as for game requests
    ([see above](#game_requests)), except that `gameid` should be used instead of `id`.

    `/game_api/v1/sales/gameid/4`

    `/game_api/v1/sales/title/shoe+lace+simulator+2000`

##### Filtering by date

Sales requests can be filtered by date as well as by games:

    `/game_api/v1/sales/startdate/2015-01-01/`

    `/game_api/v1/sales/enddate/2015-08-01/`

    `/game_api/v1/sales/startdate/2015-01-01/enddate/2015-08-01/`

### Responses

The response of GET requests is a JSON object. Rather than giving specifics about what these objects look like,
we provide you with an interactive way to figure it out yourself ([see below](#try_it)).

#### JSONP

The JSON response can be wrapped in a callback function (to get JSONP) using the 'callback' querystring option.
For example:

    `game_api/v1/games/?callback=mycallback`



The gamestore can be accessed <a href="http://gamestore2015.herokuapp.com">here</a>.

## Known issues
*Registration confirmation mail is not visible to the end-user, link added to the page as a work-around.
*Navigation bar doesn’t work optimally on Chrome Android v. 40.0, especially on the API help page.
*Service is not optimized for playing games on mobile.
*Our game, Adventure of Save Button, has a minor bug that causes highscore messages to disappear from the screen slightly too soon









    