# Description
[Gamestore 2015](http://gamestore2015.herokuapp.com) is a game service that supports uploading, modifying and playing games. To be able to use these features, the user is required to log in. There are two types of users: developers and players. A developer (belonging to the group Developers) can upload games, edit game attributes and remove his own games. A player (belonging to the group Players) can view details about and highscores of games, view related games, and purchase and, of course, play games.

A user can log in with Google login, a previously created Gamestore 2015 account, or create a completely new account. The Google login can only be used to log in as a player. When a player logs in, he is redirected to the ‘My Games’ page. Clicking a game’s name or picture redirects to a more detailed view where the user can view highscores, games sharing the same tags and more games by the same developer.

Games should implement the postmessage protocol as presented in the project description. Otherwise, gameplay itself is completely dependent on the game being played, as all of the game controls are required to be in the game. In other words, the ‘Play game’ page is nothing but a page with an iframe that listens to messages from the game and sends messages to it. There are currently two playable games: the example game and our own game, the other ‘games’ are purely fillers that make it easier to demonstrate site features.

The initial [project plan](project_plan.md) can be found [behind this link](project_plan.md).

The [final submission](final_submission.md) can be found [behind this link](final_submission.md).
