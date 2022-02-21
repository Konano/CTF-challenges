from gamedata import *
import os
import random

random.seed(os.urandom(64))

x, y = 0, 0


def elevation(x, y):
    while y < 1:
        y += WIDTH
    while 1 <= y - WIDTH:
        y -= WIDTH
    U, D = int(x-1), int(x+1)
    L, R = int(y-1), int(y+1)
    return MAP[U:D+1, L:R+1].max()


def game_init():
    global x, y
    x = 2
    y = random.randint(1, WIDTH)
    while elevation(x, y) != 0:
        y = random.randint(1, WIDTH)
    x += 0.5
    y += 0.5


dir_map = {
    'W': (-1, 0),
    'S': (1, 0),
    'A': (0, -1),
    'D': (0, 1),
}


if __name__ == '__main__':
    print('Nano Maze!')

    # Start a new game
    game_init()
    direction = ''
    while True:
        # print(x, y)  # debug mode
        __direction = input('> ')
        if len(__direction) > 0:
            direction = __direction
        try:
            assert len(direction) == 1
            assert len(direction.encode()) == 1
            direction = direction.upper()
            assert direction in 'WASD'
        except Exception as e:
            print('Invalid input')
            continue
        dx, dy = dir_map[direction]
        dx *= random.random()
        dy *= random.random()
        now = elevation(x, y)
        toward = elevation(x+dx, y+dy)
        if (min(now, toward) == -1 or now >= toward) and toward != 9:
            x += dx
            y += dy
            while y < 1:
                y += WIDTH
            while 1 <= y - WIDTH:
                y -= WIDTH
            print('Moved forward', max(abs(dx), abs(dy)))
            if min(now, toward) != -1 and now != toward:
                print('[click]')
        else:
            print('Cannot be moved')

        if elevation(x, y) == 3:
            print('Congratulation!')
            print('Here is your flag:', flag)
            break
