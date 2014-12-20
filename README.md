# CSE-C3210 Web Software Development Project Plan

## General description
We will create a webshop application for Javascript games using the Django framework. The webshop will have players who play games and developers who upload games (developers cannot be players and vice versa).

## Models

### Player
A User who can buy and play games. Cannot be Developer.
Extends Django User model.

- pk: player_id
- name
- email

### Developer
A User who can upload games. Cannot be Player.
Extends Django User model.

- pk: developer_id
- name
- email

### Game
A game that has been uploaded by a Developer and can be purchased by a Player.

- pk: game_id
- developer_id (foreign key to Developer)
- url
- price
- tags

### Highscore
A list of highscores for a game (e.g. top 10).

- game_id (foreign key to Game)
- player_id (foreign key to Player)
- score
- datetime (when the record was set)

### OwnedGame
A copy of a Game that is owned by a Player and can be played.

- player_id (foreign key to Player)
- game_id (foreign key to Game)
- gamestate (json string)

### Purchase
A record of purchase of a Game by a Player.

- player_id (foreign key to Player)
- game_id (foreign key to Game)
- datetime (when the game was bought)
- fee (how much was paid)

## Views and URLs

### Login page 
Default page, logout redirects here
url:
 
    /login


### Sign-up
create new player/developer
url: 

    /signup


### View and select owned games 
url: 

    /games

first page after login for players, view all games (separate owned games from all available games), buy games, see highscores for each game

### Play one owned game
url: 
    
    /games/gamename

### View global highscores
url: 
    
    /highscores/gamename

### Check-out
url: 
    
    /checkout

Pay for a game you plan to buy. The payments are handled by the Niksula mockup payment service.

### Developer page
url: 
    
    /dev

e.g. lists all games that the developer owns, allow uploading games, removing, editing

### Developer sales
url: 
    
    /dev/sales
    
lists sales of games by dev

### JSON(P) views for the RESTful API
base url: 
    
    /game_api/v1

2nd level url options:
    
    /tagged/tags     select game(s) by tag(s) 
    /name/names      select game(s) by name(s)
    /dev/devs        select game(s) by developer name(s)
    
tags, names, devs can be strings containing wildcards ( * ) and or expressions ( | ),  For example:
    
    /game_api/v1/tagged/action|adventure/name/dragon*

Response object(s) have the form (e.g.):
    
    { 
        name : ..., tags : [...], 
        developer : ..., number_of_owners : ..., 
        highscore : ..., times_played : ..., 
        date_uploaded : ...
    }

## Planned Features
In addition to the mandatory requirements, we plan to implement the following:

### Save/load
The save/load feature will use window.postMessage to send the game state between the game and the database as JSON data.

### 3rd party login
In addition to the django authentication and authorisation we plan to use a 3rd party login. A 3rd party login should be fairly simple to implement. We plan to use Google’s API for this.

### RESTful API
A RESTful API should not require very much effort, if it is implemented in the same way as in exercise 7.2.
The RESTful API can be used to examine games including sales, highscores, similar games etc.

### Own game
We will develop at least one game of our own for the webshop.

### Mobile-friendliness achieved through Bootstrap
We are going to use Bootstrap as the UI framework.

### Additional features:
#### Displaying related games
Our plan is to list games that the user may be interested in based on tags related to the game type. This might not be such a valuable feature if the total amount of games is small, but if the amount increases, it is a handy feature.

## Working methods and tools

### Communication and project management
We will be using a Trello board as our primary means of communication and project management. We have defined a set of color codings for the Kanban cards to distinguish between the importance of each issue. The board follows a simple “To Do-Doing-Done”-structure. Link to our board: https://trello.com/b/30jjvjap

We are also using Google Drive for tasks that require word processing and spreadsheet capabilities, such as documentation and work hour follow-up.

We are planning to work together and have face-to-face meetings approximately one afternoon per week to facilitate efficient communication.

### Frameworks, tools and resources
Python/Django will be used for server side code. For client-side code, we will be using JavaScript, and in particular the jQuery library. The design of our webshop application will be realized using the Bootstrap CSS framework. During development, we will be using an SQLite3 database, however, we will probably have to change to a Postgres database when deploying to Heroku. Git will be used for version control. We will use an HTML validator and JSHint for validation.

### Working order
We will start by creating a functioning application skeleton, to which we will add features as the project progresses. The mandatory requirements will be completed and tested first. After this, we will start polishing and implementing additional features. Some time near the end of development must be reserved for deployment to Heroku.

### Schedule
We find it difficult to estimate a timetable at this point, but we have created a rough weekly schedule as follows:

- Week 53: Set up project in Git, create and configure Django project
- Week 1: Models, Views
- Week 2: Views, Templates
- Week 3: Templates, Bootstrap, CSS
- Week 4: Javascript, Ajax, Save/load features
- Week 5-6: Fixes, Additional Features
- Week 7: Deployment, testing and fine-tuning

### Testing
Our target is to create unit tests with reasonable coverage for all new functionality in order for a feature to be completed/”done”. Naturally, the app will also be extensively tested by actually using it.

### Documentation
Special attention will be given to commenting both code and git commits. Classes and methods/functions should have sufficiently informative documentation, explaining the general purpose of the class/function and its attributes/arguments.

