rgsimulator
===========

Test how your bot behaves in certain situations. 

(latest) rgkit is needed to use it. If you don't have it, grab it from [here](https://github.com/WhiteHalmos/rgkit) and install as a module. 

Usage
----

    
    usage: rgsimulator.py [-h] [-m MAP] usercode [usercode2]
    
    Robot game simulation script.
    
    positional arguments:
      usercode           File containing first robot class definition.
      usercode2          File containing second robot class definition (optional).
    
    optional arguments:
      -h, --help         show this help message and exit
      -m MAP, --map MAP  User-specified map file.


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

Screenshots
----

![](http://i.imgur.com/SNT2dUN.png)
![](http://i.imgur.com/RN8KntI.png)

