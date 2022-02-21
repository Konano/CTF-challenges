import copy
import string
import itertools as it
from pwn import *
import json

FLAG_FORMAT = b'TQLCTF{.+}'

context(log_level='info', os='linux', arch='amd64')

if args.REMOTE:
    r = remote('47.106.193.146', 41245)
else:
    r = remote('localhost', 65101)


def move(direction):
    r.sendlineafter(b'>', direction)
    return r.recvline().decode().strip()


def up(aim=None):
    global X, Y
    with log.progress(f'U {aim}'):
        if aim is None:
            times = 0
            while times < 20:
                ret = move(b'w')
                if ret == 'Cannot be moved':
                    times += 1
                else:
                    times = 0
        else:
            while int(X) != aim:
                ret = move(b'w')
                if ret != 'Cannot be moved':
                    X -= float(ret.split(' ')[-1])
            log.success(f'{X} {Y}')


def down(aim=None):
    global X, Y
    with log.progress(f'D {aim}'):
        if aim is None:
            times = 0
            while times < 20:
                ret = move(b's')
                if ret == 'Cannot be moved':
                    times += 1
                else:
                    times = 0
        else:
            while int(X) != aim:
                ret = move(b's')
                if ret != 'Cannot be moved':
                    X += float(ret.split(' ')[-1])
            log.success(f'{X} {Y}')


def left(aim=None):
    global X, Y
    with log.progress(f'L {aim}'):
        if aim is None:
            times = 0
            while times < 20:
                ret = move(b'a')
                if ret == 'Cannot be moved':
                    times += 1
                else:
                    times = 0
        else:
            while int(Y) != aim:
                ret = move(b'a')
                if ret != 'Cannot be moved':
                    Y -= float(ret.split(' ')[-1])
                if Y < 0:
                    Y += 75
            log.success(f'{X} {Y}')


def right(aim=None):
    global X, Y
    with log.progress(f'R {aim}'):
        if aim is None:
            times = 0
            while times < 20:
                ret = move(b'd')
                if ret == 'Cannot be moved':
                    times += 1
                else:
                    times = 0
        else:
            while int(Y) != aim:
                ret = move(b'd')
                if ret != 'Cannot be moved':
                    Y += float(ret.split(' ')[-1])
            log.success(f'{X} {Y}')

up()
right()
X = 2
Y = 8
left(10)
down(17)
right(16)
down(19)
right(34)
up(10)
right(39)
down(14)
right(43)
down(19)
right(52)
up(7)
right(65)
down(28)
left(61)
down(30)
left(52)
down(35)
right(57)
down(42)
left(44)
up(37)
left(34)
down(40)
left(21)
up(34)
left(15)
down(40)
left(8)
down(45)
right(41)

r.recvuntil(b'Here is your flag: ')
flag = r.recvregexS(FLAG_FORMAT)
log.success(f'Flag: {flag}')
