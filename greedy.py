#!/usr/bin/python
# greedy.py
# Copyright (C) 2011 by Shawn Yarbrough
# May be used for non-commerical purposes. May NOT be modified.
# TODO: Pick a better software license!
#
# A simple dungeon game with a text map.

import curses, sys, traceback, signal, os, time, random
import utility

# got_signal
# Flag set if a signal is caught (ex: user presses ctrl-C).
got_signal = False
def signal_handler(num, frame):
    global got_signal
    got_signal = True
signal.signal(signal.SIGINT,signal_handler)
signal.signal(signal.SIGTERM,signal_handler)

# reset_screen
# Function called to return the screen to normal line-by-line input mode.
def reset_screen():
    try:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    except:
        pass

# Entity
class Entity(object):
    # __init__
    def __init__(self,xx,yy,ch):
        self.xx = xx
        self.yy = yy
        self.code = ch
        self.inventory = []
        self.container = None

    def name(self):
        return utility.readable_name(self.__class__.__name__)

# Item
class Item(Entity):
    # __init__
    def __init__(self,xx,yy,ch):
        Entity.__init__(self,xx,yy,ch)

# Money
class Money(Item):
    # __init__
    def __init__(self,xx,yy,count):
        Item.__init__(self,xx,yy,'$')
        self.count = count

# Wall
class Wall(Entity):
    # __init__
    def __init__(self,xx,yy,ch):
        Entity.__init__(self,xx,yy,ch)

# Character
class Character(Entity):
    # __init__
    def __init__(self,xx,yy,ch,hp,stat_str,stat_spd):
        Entity.__init__(self,xx,yy,ch)
        self.hit_points = hp
        self.max_hit_points = hp
        self.stat_str = int(stat_str)
        self.stat_spd = float(stat_spd)
        self.dead = False

    # attack
    def attack(self,ee,game):
        if self.dead: return;
        dmg = self.stat_str
        ee.hit_points -= dmg
        txt = (self.name()+' attacked '+ee.name()+' for '+str(dmg)+
              ' damage')
        if ee.hit_points <= 0:
            ee.dead = True
            txt += ', a killing blow!'
        else:
            txt += '.'
        game.console.append(txt)
        if ee.dead and ee is game.player:
            game.console.append('You have died.')
        return ee.dead

    # pickup
    def pickup(self,ee,game):
        self.inventory.append(ee)
        ee.container = self
        return True

    # push
    def push(self,ee,game):
        raise Exception('TODO: Finish writing the Character.push() function.')

    def move(self,dx,dy,game):
        """Move a character in one of eight directions."""
        nx, ny = self.xx+dx, self.yy+dy
        if nx < 0 or nx >= len(game.dungeon[0]): return False;
        if ny < 0 or ny >= len(game.dungeon): return False;
        if game.dungeon[ny][nx] != '.':
            return False
        for ee in game.entities:
            if ee.xx == nx and ee.yy == ny:
                if isinstance(ee,Character):
                    if self.attack(ee,game): break;
                elif isinstance(ee,Item):
                    if self.pickup(ee,game): break;
                elif isinstance(ee,Wall):
                    if self.push(ee,game): break;
                return False
        self.xx = nx
        self.yy = ny
        return True

# Player
class Player(Character):
    # __init__
    def __init__(self,xx,yy):
        Character.__init__(self,xx,yy,'@',10,2,1)

# Monster
class Monster(Character):
    # __init__
    def __init__(self,xx,yy,ch,hp,stat_str,stat_spd):
        Character.__init__(self,xx,yy,ch,hp,stat_str,stat_spd)
#       self.xtravel = random.randint(-1,+1)
#       self.ytravel = random.randint(-1,+1)
        self.travel = []

# Imp Monster
class Imp(Monster):
    # __init__
    def __init__(self,xx,yy):
        Monster.__init__(self,xx,yy,'i',5,1,0.5)

# Game
class Game(object):
    # __init__
    def __init__(self,level_file_name):
        # Game variables.
        self.dungeon=[]
        self.entities=[]
        self.player = None
        self.quit = False
        self.console = utility.Console()
        self.console.append('Welcome to Greedy Dungeon Treasure Hunter (TM)!')
        self.console.append('Copyright (C) 2011 by Shawn Yarbrough')
        self.console.append('(Press Q at any time to quit the game.)')
        self.console.append('')

        # Start up CURSES.
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_BLUE)
#       self.screen.nodelay(1)
        self.screen.leaveok(0)
        self.screen.keypad(1)
        self.screen.clear()
        self.screen.refresh()

        # Layout dimensions for the CURSES screen.
        self.map_ysize, self.map_xsize = (0,0)
        self.size_window()

        # Load the text map.
        self.dungeon=[]
        fil = open(level_file_name,'r')
        for lin in fil:
            lin = lin.rstrip('\n\r')
            self.dungeon.append(lin)
            if self.map_xsize != 0:
                if len(lin) != self.map_xsize:
                    raise Exception('Map must be rectangular. See line #'+
                          str(len(dungeon))+' of "'+level_file_name+'".')
            else:
                self.map_xsize = len(lin)
        self.map_ysize = len(self.dungeon)

        # Strip all entities out of the text map and spawn them.
        dungeon2 = []
        for lin in self.dungeon:
            my = len(dungeon2)
            dungeon2.append("")
            mx = 0
            for ch in lin:
                if ch == '@':
                    self.player = Player(mx,my)
                    self.entities.append(self.player)
                    ch = '.'
                elif ch == 'i':
                    self.entities.append(Imp(mx,my))
                    ch = '.'
                elif ch == '$':
                    self.entities.append(Money(mx,my,1))
                    ch = '.'
                dungeon2[-1] += ch
                mx += 1
        self.dungeon = dungeon2
        if self.player == None:
            raise Exception('Player not found. (Put exactly one'+
                            ' "@" on the map somewhere.)')

    # __del__
    def __del__(self):
        reset_screen()

    # size_window
    def size_window(self):
        self.screen_ysize, self.screen_xsize = self.screen.getmaxyx()

        self.console_xsize = self.screen_xsize
        self.console_ysize = 5+(self.screen_ysize%2)

        self.bar_xsize = 41+(self.screen_xsize%2)
        self.bar_ysize = self.screen_ysize-self.console_ysize

        self.view_xsize = self.screen_xsize-self.bar_xsize    # Always odd.
        self.view_ysize = self.bar_ysize                      # Always odd.

    # run_keyboard
    def run_keyboard(self):
        ch = self.screen.getch()
        if ch == ord('q') or ch == ord('Q'):    # Quit game.
            self.quit = True
        elif ch == 27:    # Quit game.
            self.quit = True
        elif ch == curses.KEY_RESIZE:
            self.size_window()
            self.screen.clear()

        if not self.player.dead:
            if ch == curses.KEY_LEFT:
                self.player.move(-1,0,self)
            elif ch == curses.KEY_RIGHT:
                self.player.move(+1,0,self)
            elif ch == curses.KEY_UP:
                self.player.move(0,-1,self)
            elif ch == curses.KEY_DOWN:
                self.player.move(0,+1,self)

    def movable(self,nx,ny):
        """Decide if a location is movable-to.
        
        Location must be on the map, not a wall, not occupied by an entity.
        """
        if nx < 0 or nx >= len(self.dungeon[0]): return False;
        if ny < 0 or ny >= len(self.dungeon): return False;
        if self.dungeon[ny][nx] != '.':
            return False
        for ee in self.entities:
            if ee.xx == nx and ee.yy == ny: return False;
        return True

    def attackable(self,nx,ny):
        """Decide if a location is attackable.
        
        Location must be on the map, not a wall, occupied by a Character.
        """
        if nx < 0 or nx >= len(self.dungeon[0]): return False;
        if ny < 0 or ny >= len(self.dungeon): return False;
        if self.dungeon[ny][nx] != '.':
            return False
        for ee in self.entities:
            if ee.xx == nx and ee.yy == ny:
                if isinstance(ee,Character):
                    return True
                return False
        return True

    def path_movable(self,path):
        """Decide if a whole path is movable-to each step along the way."""
        for point in path:
            if not self.movable(*point): return False;
        return True

    def run_ai(self):
        """Run the artifical intelligence logic."""
        first = True
        for ee in self.entities:
            if not isinstance(ee,Monster): continue;

            # Check if the monster has line-of-sight to the player.
            ppath = utility.line(ee.xx,ee.yy,self.player.xx,self.player.yy)
            if len(ppath) > 2:
                del ppath[0]
                del ppath[-1]
                if self.path_movable(ppath):
                    ee.travel = ppath    # Chase and attack the player.

            # We are next to the player. Attack.
            else:
                ee.attack(self.player,self)
                continue

            # Pick a random direction to travel if we have no path yet
            # and aren't next to the player.
            if len(ee.travel) == 0 and len(ppath) > 0:
                ii = 0
                while True:
                    xx = random.randint(-10,+10)
                    yy = random.randint(-10,+10)
                    ee.travel = utility.line(ee.xx,ee.yy,ee.xx+xx,ee.yy+yy)
                    del ee.travel[0]
                    if self.path_movable(ee.travel):
                        break;
                    ii += 1
                    if ii >= 5: ee.travel = []; break;

            # Move to the next step along the path.
            if len(ee.travel) > 0:
                tr = ee.travel[0]
                if self.movable(*tr):
                    ee.move(tr[0]-ee.xx,tr[1]-ee.yy,self)
                    del ee.travel[0]
                    continue

    @staticmethod
    def keep_entity(ee):
        """Decide whether or not to keep an entity in the main entity list.
        
        If it's a dead character, no we don't keep it.
        If it's an item in a container, no we don't keep it.
        """
        if isinstance(ee,Character) and ee.dead: return False;
        if isinstance(ee,Item) and ee.container != None: return False;
        return True

    # run_entity_clean_up
    def run_entity_clean_up(self):
        self.entities[:] = [ee for ee in self.entities if Game.keep_entity(ee)]

    # run_draw
    def run_draw(self):
        self.screen.erase()

        # Map.
        xmin = self.player.xx-int(self.view_xsize/2)
        xmax = xmin+self.view_xsize-1

        ymin = self.player.yy-int(self.view_ysize/2)
        ymax = ymin+self.view_ysize-1

        vx0,vy0 = xmin,ymin

        if xmin < 0: xmin = 0;
        if xmax >= self.map_xsize: xmax = self.map_xsize-1;

        if ymin < 0: ymin = 0;
        if ymax >= self.map_ysize: ymax = self.map_ysize-1;

        for yy in range(0,self.view_ysize):
            self.screen.addstr(yy,0,' '*self.view_xsize,curses.color_pair(1))

        # Draw map tiles.
        for yy in range(ymin,ymax+1):
            lin = self.dungeon[yy][xmin:xmax+1]
            self.screen.addstr((yy-ymin)+(ymin-vy0),
                               (xmin-vx0),lin,curses.color_pair(1))

#       # Draw AI paths.
#       for ee in self.entities:
#           if not isinstance(ee,Monster): continue;
#           for point in ee.travel:
#               xx = point[0]-vx0
#               yy = point[1]-vy0
#               self.screen.addstr(yy,xx,'?',curses.color_pair(1))

        # Draw map entities.
        for ee in self.entities:
            xx = ee.xx-vx0
            yy = ee.yy-vy0
            if xx < 0 or xx > self.view_xsize: continue;
            if yy < 0 or yy > self.view_ysize: continue;
            self.screen.addstr(yy,xx,ee.code,curses.color_pair(1))

        # Console.
        contxt = self.console.show(5,self.console_xsize)
        for ii in range(0,5):
            self.screen.addstr(self.screen_ysize-self.console_ysize+
                               ii,0,contxt[ii])

        # Cursor.
        self.screen.move((self.view_ysize-1)/2,(self.view_xsize-1)/2)
        self.screen.refresh()

    # run
    def run(self):
        self.run_draw()
        global got_signal
        while not self.quit and not got_signal:
            if not self.player.dead:
                self.run_keyboard()
                self.run_ai()
                self.run_entity_clean_up()
                self.run_draw()
            else:
                self.run_keyboard()
                self.run_draw()

# main
def main():
    if len(sys.argv) > 2:
        print "Usage: "+sys.argv[0]+" [game]"
        print "    Where [game] is a folder name in the ./dungeons/ folder."

    # Locate the game.
    game_directory_name = 'greedy'
    if len(sys.argv) == 2:
        game_directory_name = sys.argv[1]
    game_path = 'dungeons/'+game_directory_name

    levels = os.listdir(game_path)
    levels.sort()
    if len(levels) == 0: return;
    level_path = game_path+'/'+levels[0]

    # Play the game.
    Game(level_path).run()

if __name__ == '__main__':
    try:
        main()
    except:
        reset_screen()
        traceback.print_exc()

