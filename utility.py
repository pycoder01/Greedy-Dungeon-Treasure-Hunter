# utility.py
# Copyright (C) 2011 by Shawn Yarbrough

def line(x0,y0,x1,y1):
    """ Bresenham's line drawing algorithm."""
    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)

    linex = []
    liney = []

    dx = abs(x1-x0)
    dy = abs(y1-y0)

    sx,sy = 0,0

    if x0 < x1:
        sx = 1
    else:
        sx = -1

    if y0 < y1:
        sy = 1
    else:
        sy = -1;

    err = dx-dy

    while True:
        linex.append(x0)
        liney.append(y0)

        if x0 == x1 and y0 == y1: break;

        e2 = 2*err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return zip(linex,liney)

