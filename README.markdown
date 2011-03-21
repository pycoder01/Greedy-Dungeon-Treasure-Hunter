Greedy Dungeon Treasure Hunter (TM)
===================================

A simple text dungeon game. The look-and-feel is similar to [Nethack](http://www.nethack.org/), except that Greedy centers the map view on the player and scrolls around as the player moves.

Written in Python for fun. Tested on Linux in an xterm window -- actually GNOME Terminal on Ubuntu. Uses the CURSES text library. Does NOT work on Microsoft Windows because CURSES is not yet available there for Python.

TODO:

* Test over a remote SSH connection. (May be slow due to the map scrolling.)
* Display the player's stats such as hit points and strength.
* Display the player's inventory.
* Add stairs to go to the next level.
* Do line-of-sight checks instead of the whole map being visible.
* More monsters.
* More items.
* Switch from CURSES to a modern GUI library. Maybe use [Pygame](http://www.pygame.org/).

