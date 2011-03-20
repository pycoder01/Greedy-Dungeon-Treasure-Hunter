# utility.py
# Copyright (C) 2011 by Shawn Yarbrough

def line(x0,y0,x1,y1):
    """ Bresenham's line drawing algorithm."""
    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)

    path = []

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
        path.append((x0,y0))

        if x0 == x1 and y0 == y1: break;

        e2 = 2*err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return path

def readable_name(class_name,sep=' '):
    """Break a string apart at any uppercase letters."""
    answer = ''
    first = True
    for ch in class_name:
        if ch.isupper() and not first:
            answer += sep
        if first: first = False;
        answer += ch
    return answer

class Console(list):
    """A text console for displaying messages and scrolling them."""
    def __init__(self):
        pass

    def show(self,count,width,pad=True):
        """Return a list of the last 'count' lines, wrapped to 'width'.
    
        If 'pad' is true, will always return 'count' lines, even if the
        console is empty meaning blank lines must be generated and appended.
        """
        answer = []
        lin = len(self)-1
        while lin >= 0 and len(answer) < count:
            wrapped = [self[lin][index:index+width]
                for index in range(0,len(self[lin]),width)]
            while len(wrapped) > 0 and len(answer) < count:
                answer.append(wrapped.pop())
            lin -= 1
        answer.reverse()
        if pad:
            while len(answer) < count:
                answer.append('')
        return answer

