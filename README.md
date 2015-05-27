rgsimulator
===========

Test how your [robotgame](https://robotgame.net/) bot behaves in certain situations.

(latest) rgkit is needed to use it. If you don't have it, grab it from [here](https://github.com/RobotGame/rgkit) and install as a module with pip.

Usage
----

    usage: rgsimulator.py [-h] [-m MAP] player [player2]

    Robot game simulation script.

    positional arguments:
      player             File containing first robot class definition.
      player2            File containing second robot class definition (optional).

    optional arguments:
      -h, --help         show this help message and exit
      -m MAP, --map MAP  User-specified map file.

If your robot code contains a dict called `rgsim_text`, rgsimulator will attempt to print the dict's values at the location given by the dict's keys.

Controls
----

rgsimulator is fully keyboard-controlled.

* Use arrow keys or `WASD` to move selection.
* Press `F` to create a friendly bot in selected cell.
* Press `E` to create an enemy bot in selected cell.
* Press `R`, `Delete` or `Backspace` to remove a bot in selected cell.
* Press `H` to change hp of a bot in selected cell.
* Press `T` to change turn.
* Press `C` to clear the board.
* Press `Space` to show moves bots would attempt.
* Press `Enter` to progress turn.
* Press `L` to load a match from robotgame.net. Enter just the match number.
* Press `K` to load a specific turn from a loaded match. Also updates the simulator turn counter.
* Press `P` to swap code for the two bots. (player 1 becomes player 2)
* Press `O` to reload the code for both bots.
* Press `N` to change the action of the robot in selected cell. Think `N` for "next action".
* Press `G` to spawn robots and remove robots in spawn locations. Think `G` for "generate robots".

Screenshots
----

![](http://i.imgur.com/SNT2dUN.png)
![](http://i.imgur.com/RN8KntI.png)
