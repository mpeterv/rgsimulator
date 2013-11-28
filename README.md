rgsimulator
===========

Test how your bot behaves in certain situations. 

Usage
----

    
    usage: rgsimulator.py [-h] [-m MAP] usercode
    
    Robot game simulation script.

    positional arguments:
      usercode           File containing robot class definition.
    
    optional arguments:
      -h, --help         show this help message and exit
      -m MAP, --map MAP  User-specified map file.

Controls
----

rgsimulator is fully keyboard-controlled.

* Use arrow keys or `WASD` to move selection.
* Press `F` to create a friendly bot in selected cell. 
* Press `E` to create an enemy bot in selected cell. 
* Press `R`, `Delete` or `BackSpace` to remove a bot in selected cell. 
* Press `H` to change hp of a bot in selected cell. 
* Press `T` to change turn. 
* Press `Space` or `Enter` to run simulation. 

