MassTris is a lightweight and scaling implementation of Tetris from scratch, for the twin purposes of fun and education.
MassTris is designed to allow a LOT of people to mass together in a single multiplayer tetris game with as little
overhead and as few requirements and dependencies as possible.




==> Requirements <==
Python >= 3.6 (see python.org for details for your system)
Pygame ("python -m pip install -U pygame --user" or see pygame.org)



==> Quick Setup <==
Open "configuration.txt"
Set Fullscreen mode True/False
Set Resolution for windowed mode
Assign keyboard1 and keyboard2 to players that will use the keyboard.
Examples:
 Solo game with gamepad: Set keyboard1 to 2 and keyboard2 to 3
 Game with first player on keyboard, second and third players on gamepads: Set keyboard1 to 1, keyboard2 to 4
Note: Networking is very experimental and unstable recommended left off




==> How to play <==
Menu:
  keyboard:
    left/right/a/d to adjust number of local players
    up/down/w/s to select options
    i/q/e to turn CPU players on or off
    return/space to confirm selection
    escape to quit
  joystick/gamepad:
    left/right to adjust number of local players
    up/down to select options
    Y/Button 3 to turn CPU players on or off
    A/Button 0 to confirm selection
    B/Button 1 to quit

Gameplay (All can be changed in "configuration.txt"):
  Default Keyboard 1:
    a/d to move piece
    e to store/swap current tetramino
    space to fast drop the current tetramino
    n/m to rotate
    q to highlight game
    s to speed up dropping speed
    return to pause
  Default Keyboard 2:
    left/right to move piece
    up/down to select options
    backspace to store/swap current tetramino
    down to fast drop the current tetramino
    o/p to rotate
    i to highlight game
    up to speed up dropping speed
  Joystick/Gamepad:
    left/right to move piece
    Y/Button 3 to store/swap current tetramino
    A/Button 0 to fast drop the current tetramino
    B/Button and X/Button 2 to rotate
    LB/Button 4 to highlight game
    RB/Button 5 to speed up dropping speed
    START to pause



==> Configuration <==
Settings can be changed in "configuration.txt", reset to default by deleting the file.
Important Settings:
FullScreen on/off
Resolution for windowed mode
Max Games has no hard limit... the difference between the number of players and the cap will be made up by AI if turned on
Performance of the system and size of the display required are left up to the user.
As many keyboard configurations as wanted can be added by following patterns for keyboard 1 and 2.
All gamepads and joysticks detected will be assigned to the other players



==> Customizing Assets <==
Music:
Drop in any *.ogg music files in the data/music folder and it will be randomly selected to play during gameplay.
The menu.ogg file is the track played on menu screen.

Backgrounds:
Drop in wallpapers in the data/backgrounds folder to be randomly displayed during games.
*.jpg format recommended

==> License Information <==
Menu track:
The Pirate and the Dancer by Rolemusic on Enough Records
(converted to .ogg)

Other included tracks for demonstration:
Epic Song by BoxCat Games
Battle (Boss) by BoxCat Games
Breaking In by BoxCat Games
(converted to .ogg)

Included background images courtesy of NASA.

