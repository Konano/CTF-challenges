BANNER = '''
                                        $$\   $$\           $$\                                                    
                                        $$ |  $$ |          \__|                                                   
$$$$$$$\   $$$$$$\  $$$$$$$\   $$$$$$\  $$ |  $$ |$$$$$$$\  $$\ $$\    $$\  $$$$$$\   $$$$$$\   $$$$$$$\  $$$$$$\  
$$  __$$\  \____$$\ $$  __$$\ $$  __$$\ $$ |  $$ |$$  __$$\ $$ |\$$\  $$  |$$  __$$\ $$  __$$\ $$  _____|$$  __$$\ 
$$ |  $$ | $$$$$$$ |$$ |  $$ |$$ /  $$ |$$ |  $$ |$$ |  $$ |$$ | \$$\$$  / $$$$$$$$ |$$ |  \__|\$$$$$$\  $$$$$$$$ |
$$ |  $$ |$$  __$$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  \$$$  /  $$   ____|$$ |       \____$$\ $$   ____|
$$ |  $$ |\$$$$$$$ |$$ |  $$ |\$$$$$$  |\$$$$$$  |$$ |  $$ |$$ |   \$  /   \$$$$$$$\ $$ |      $$$$$$$  |\$$$$$$$\ 
\__|  \__| \_______|\__|  \__| \______/  \______/ \__|  \__|\__|    \_/     \_______|\__|      \_______/  \_______|
                                                                                                                   
                                                                                                                   
Caught in the Dark ......

You're piloting a spaceship in a dark, two-dimensional universe. Your ship can only move in four directions: north(W), south(S), east(D) and west(A). You can't see anything, but you can feel the walls around you if you touch them.
'''

import random

w = 75
h = 51

MAP = [list(x) for x in open('map.txt', 'r').read().strip().split('\n')]
FLAG_1 = "TPCTF{NO7icE-And-HELP-THe-vIsUALLy-1MP@IR3d-ar0unD-US}"

flag_chips = [[0 for _ in range(w)] for _ in range(h)]
flag_chips_id = [x+1 for x in range(len(FLAG_1))]
random.Random(FLAG_1).shuffle(flag_chips_id)
for i in range(h):
    for j in range(w):
        if MAP[i*2+1][j*2+1] == '$':
            flag_chips[i][j] = flag_chips_id[-1]
            del flag_chips_id[-1]
assert len(flag_chips_id) == 0

flag = ['_' for _ in range(len(FLAG_1))]
# flag is: ______________________________________________________

x, y, c = (25, 37, 0)
fuel = 1000

print(BANNER)
while fuel > 0:
    print(f'Fuel: {fuel}')
    print()
    def move(d):
        global x, y, c, fuel
        __x = x * 2 + 1 + [-1, 1, 0, 0][d]
        __y = y * 2 + 1 + [0, 0, -1, 1][d]
        # print(x, y, __x, __y)
        if MAP[__x][__y] in '-|':
            fuel -= 3
            print("Sorry you hit the wall.")
            return
        if MAP[__x][__y] in 'AB':
            if c and (c == 1) != (MAP[__x][__y] == 'A'):
                fuel -= 3
                print("Sorry you hit the wall.")
                return
            __c = 1 if MAP[__x][__y] == 'A' else 2
        __x = x * 2 + 1 + [-1, 1, 0, 0][d] * 2
        __y = y * 2 + 1 + [0, 0, -1, 1][d] * 2
        x += [-1, 1, 0, 0][d]
        y += [0, 0, -1, 1][d]
        # print(__x, __y, MAP[__x][__y])
        if MAP[__x][__y] == ' ' or MAP[__x][__y] == 'x':
            c = 0
            fuel -= 1
            print("Nothing happened.")
            return
        if MAP[__x][__y] == '$':
            c = 0
            fuel -= 1
            if flag[flag_chips[__x//2][__y//2] - 1] == '_':
                fuel += 50
                flag[flag_chips[__x//2][__y//2] - 1] = FLAG_1[flag_chips[__x//2][__y//2] - 1]
                print("You get the flag fragment!", 'Now the flag is ' + ''.join(flag))
            else:
                print("Nothing happened.")
            return
        if MAP[__x][__y] == '#':
            c = 0
            fuel -= 1
            x = random.randint(0, h-1)
            y = random.randint(0, w-1)
            while MAP[x*2+1][y*2+1] != ' ':
                x = random.randint(0, h-1)
                y = random.randint(0, w-1)
            print("It seems you've been randomly transported somewhere.")
            return
        if MAP[__x][__y] == '*':
            c = __c if c == 0 else c
            fuel -= 1
            print("Nothing happened.")
            return
        raise RuntimeError('anything wrong?')
    for d in input("> ").strip().upper():
        if d in 'WSAD':
            move('WSAD'.index(d))
        if fuel <= 0:
            break
    print()

print('Your spaceship crashed.')
