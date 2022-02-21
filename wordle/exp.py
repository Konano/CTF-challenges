import copy
import random
from pwn import *
from randcrack import RandCrack

with open('valid_words.txt', 'r') as f:
    valid_words = [x.strip() for x in f.readlines()]

FLAG_FORMAT = b'TQLCTF{.+}'

context(log_level='info', os='linux', arch='amd64')

if args.REMOTE:
    r = remote('47.106.193.146', 44116)
else:
    r = remote('localhost', 65100)

def square_translate(s):
    color = {
        b'\033[42m  \033[0m': 'G',
        b'\033[43m  \033[0m': 'Y',
        b'\033[47m  \033[0m': 'W',
        b' ': '',
    }
    ret = ''
    while len(s):
        for color_bytes in color.keys():
            if s.startswith(color_bytes):
                ret += color[color_bytes]
                s = s[len(color_bytes):]
    return ret

rc = RandCrack()

def predict_challenge():
    return valid_words[rc.predict_randrange(len(valid_words) * (2 ** 20)) % len(valid_words)]

with log.progress('Stage 1: Get random bits in easy mode and check'):
    for _ in range(2):
        r.sendlineafter(b'> ', b'0')
        progress = log.progress('Easy mode')
        for round_id in range(512):
            progress.status(f'Round {round_id} / 512')
            r.recvuntil(b'#')
            first = r.recvline()
            available = copy.deepcopy(valid_words)
            if not rc.state:
                while True:
                    word = random.choice(available)
                    r.sendlineafter(b'> ', word.encode())
                    checked = r.recvuntil(b'!').decode()
                    if checked == 'Wrong!':
                        checked = square_translate(r.recvline().strip())
                        log.debug(checked)
                        for i in range(5):
                            if checked[i] == 'G':
                                available = list(filter(lambda x: x[i] == word[i], available))
                            else:
                                available = list(filter(lambda x: x[i] != word[i], available))
                    else:
                        last = valid_words.index(word)
                        break
                rand_32 = (int(first, 16) ^ last) * len(valid_words) + last
                rc.submit(rand_32)
            else:
                r.sendlineafter(b'> ', predict_challenge().encode())
                checked = r.recvuntil(b'!').decode()
                if checked == 'Wrong!':
                    log.failure('Failed')
                    exit(0)
        progress.success(f'Round 512 / 512')
    log.success('Success')

with log.progress('Stage 2: Solved in hard mode'):
    r.sendlineafter(b'> ', b'3')
    progress = log.progress('Hard mode')
    for round_id in range(512):
        progress.status(f'Round {round_id} / 512')
        r.recvuntil(b'#')
        r.recvline()
        r.sendlineafter(b'> ', predict_challenge().encode())
        checked = r.recvuntil(b'!').decode()
        if checked == 'Wrong!':
            log.failure('Failed')
            exit(0)
    progress.success(f'Round 512 / 512')
    log.success('Success')

flag = re.findall(FLAG_FORMAT, r.recvregex(FLAG_FORMAT))[0].decode()
log.info(f'flag: {flag}')
