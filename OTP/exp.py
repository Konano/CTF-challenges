import copy
import string
import itertools as it
from pwn import *
import json
import hashlib


def proof_of_work_2(suffix, hash): # sha256, suffix, known_hash
    judge = lambda x: hashlib.sha256(x.encode()+suffix).digest().hex() == hash
    return util.iters.bruteforce(judge, string.ascii_letters+string.digits, length=4).encode()

FLAG_FORMAT = b'TQLCTF{.+}'

context(log_level='info', os='linux', arch='amd64')

if args.REMOTE:
    r = remote('47.106.193.146', 47365)
    r.recvuntil(b'sha256(XXXX+')
    suffix = r.recv(16)
    r.recvuntil(b' == ')
    hash = r.recv(64).decode()
    r.sendlineafter(b'Give me XXXX:', proof_of_work_2(suffix, hash))
else:
    r = remote('localhost', 65100)


r.recvuntil(b'flag: ')
flag_hex = r.recvline().strip().decode()
log.info(f'flag: {flag_hex}')
flag_enc = bytes.fromhex(flag_hex)
flag_enc, flag_token_1 = flag_enc[:-4], flag_enc[-4:]

valid_char = string.digits + string.ascii_letters + string.punctuation

FLAG_LEN = len(flag_enc)-4
FLAG_TOKEN_LEN = len(flag_enc)


class InvalidChar(Exception):
    pass


def rebuild():
    global flag_hex, flag_enc, flag_token_1
    r.sendlineafter(b'> ', b'2')
    r.recvuntil(b'flag: ')
    flag_hex = r.recvline().strip().decode()
    log.info(f'flag: {flag_hex}')
    flag_enc = bytes.fromhex(flag_hex)
    flag_enc, flag_token_1 = flag_enc[:-4], flag_enc[-4:]


def encrypt(s: str) -> bytes:
    log.debug(f'enc: {s}')
    r.sendlineafter(b'> ', b'0')
    r.sendlineafter(b'> ', s.encode())
    r.recvuntil(b'message: ')
    return bytes.fromhex(r.recvline().decode())


def decrypt(s: bytes) -> str:
    log.debug(f'dec: {s.hex().encode()}')
    r.sendlineafter(b'> ', b'1')
    r.sendlineafter(b'> ', s.hex().encode())
    ret = r.recvuntil(b'message').split(b'\n')[-1]
    if ret == b'The original message':
        r.recvuntil(b'pos ')
        pos = int(r.recvline().strip().decode())
        raise InvalidChar(pos)
    r.recvuntil(b': ')
    return r.recvline().decode()


def check(s: bytes) -> int:
    try:
        decrypt(s)
        return len(s)-8
    except InvalidChar as e:
        return int(str(e))


def check_shuffle(s: bytearray, token: bytes) -> int:
    r = check(bytes(s) + token)
    log.debug(f'{(bytes(s) + token).hex()} {r}')
    return r


def get_query_seq(a):
    ret = []
    b = list(range(len(a)))
    for x in reversed(range(1, len(a))):
        idx = b.index(a[x])
        b[idx], b[x] = b[x], b[idx]
        assert b[x] == a[x]
        ret.append((x+1, idx))
    return ret


try:
    with open('shuffle_database.json', 'r') as f:
        crack_shuffle_database = json.load(f)
except:
    crack_shuffle_database = {}


def update_datebase(key, value):
    global crack_shuffle_database
    crack_shuffle_database[f'{key[0]}_{key[1].hex()}'] = value
    with open('shuffle_database.json', 'w') as f:
        json.dump(crack_shuffle_database, f)


def crack_shuffle(o: int, token: bytes):
    if crack_shuffle_database.get(f'{o}_{token.hex()}') is not None:
        return crack_shuffle_database[f'{o}_{token.hex()}']
    while True:
        msg = bytearray(os.urandom(o))
        if check_shuffle(msg, token) == 0:
            break

    log.info(f'len {o}, shuffle token {token.hex()}')

    pos_known = []
    pos_token = []
    pos = []
    progress = log.progress(f'crack_shuffle')

    # find pos_0
    while len(pos) == 0:
        progress.status(f'{pos_token} {len(pos)}/{o-4} {pos}')
        for i in range(o):
            if i not in pos_known:
                msg[i] = os.urandom(1)[0]
                if check_shuffle(msg, token) == 1:
                    is_pos_0 = True
                    counter = {0: 0, 1: 0}
                    for j in range(256):
                        msg[i] = j
                        checked = check_shuffle(msg, token)
                        if not 0 <= checked <= 1:
                            is_pos_0 = False
                            break
                        counter[checked] += 1
                    is_pos_0 &= counter[1] == len(valid_char)
                    if is_pos_0:
                        pos.append(i)
                        pos_known.append(i)
                        progress.status(f'{pos_token} {len(pos)}/{o-4} {pos}')
                        break
                    else:
                        pos_token.append(i)
                        pos_token = sorted(pos_token)
                        pos_known.append(i)
                        progress.status(f'{pos_token} {len(pos)}/{o-4} {pos}')
                while check_shuffle(msg, token) > 0:
                    msg[i] = os.urandom(1)[0]

    # find pos_token
    while check_shuffle(msg, token) == 0:
        msg[pos[0]] = os.urandom(1)[0]
    while len(pos_token) < 4:
        progress.status(f'{pos_token} {len(pos)}/{o-4} {pos}')
        for i in range(o):
            if i not in pos_known:
                msg[i] = os.urandom(1)[0]
                if check_shuffle(msg, token) == 0:
                    pos_token.append(i)
                    pos_token = sorted(pos_token)
                    pos_known.append(i)
                    progress.status(f'{pos_token} {len(pos)}/{o-4} {pos}')
                    if len(pos_token) == 4:
                        break
                    while check_shuffle(msg, token) == 0:
                        msg[pos[0]] = os.urandom(1)[0]
    progress.status(f'{pos_token} {len(pos)}/{o-4} {pos}')

    # find pos_other
    while check_shuffle(msg, token) != 1:
        msg = bytearray(os.urandom(o))
    for i in range(1, o-4):
        progress.status(f'{pos_token} {len(pos)}/{o-4} {pos}')
        while len(pos) == i:
            for j in range(o):
                if j not in pos_known:
                    msg[j] = os.urandom(1)[0]
                    r = check_shuffle(msg, token)
                    if r != i:
                        if r == i+1:
                            pos.append(j)
                            pos_known.append(j)
                            break
                        msg[j] = os.urandom(1)[0]
                        while check_shuffle(msg, token) != i:
                            msg[j] = os.urandom(1)[0]
    progress.success(f'{pos_token} {pos}')

    query_seqs = []
    for e in it.permutations(pos_token, 4):
        r = [None] * o
        for i in range(o-4):
            r[pos[i]] = i
        for i in range(o-4, o):
            r[e[i-o+4]] = i
        query_seqs.append(get_query_seq(r))

    update_datebase((o, token), query_seqs)
    return query_seqs


def correlation_2(x0, x1):
    ret, now = [], x1[0][0]-1
    p0, p1 = 0, 0
    while p0 < len(x0) and p1 < len(x1):
        if x1[p1][0].bit_length() > x0[p0][0].bit_length():
            diff = x1[p1][0].bit_length() - x0[p0][0].bit_length()
            if diff > 1:
                return  # give up
            if now.bit_length() == x1[p1][0].bit_length():
                v = x1[p1][1] // 2
                if x0[p0][0] > v:
                    while p0 < len(x0) and v != x0[p0][1]:
                        if x1[p1][1] < x0[p0][1]*2 < x0[p0][1]*2+1 < x1[p1][0]:
                            return
                        p0 += 1
                    if p0 == len(x0):
                        continue
                    if now > x1[p1][1]:
                        ret.append((now, x1[p1][1]))
                        now -= 1
                    p0 += 1
                    p1 += 1
                    continue
                else:
                    if now > x1[p1][1]:
                        ret.append((now, x1[p1][1]))
                        now -= 1
                    p1 += 1
                    continue
            if now.bit_length() == x0[p0][0].bit_length():
                if now > x0[p0][0]+1 or (x0[p0][0] == 2 and now == 3):
                    return  # give up
                v = x1[p1][1] // 2
                while p0 < len(x0) and v != x0[p0][1]:
                    ret.append((now, x0[p0][1]))
                    now -= 1
                    p0 += 1
                if p0 == len(x0):
                    continue
                ret.append((now, x0[p0][1]))
                now -= 1
                p0 += 1
                p1 += 1
                continue
        if x0[p0][1] != x1[p1][1]:
            if x0[p0][0] > x1[p1][1]:
                return
            if now > x1[p1][1]:
                ret.append((now, x1[p1][1]))
                now -= 1
            p1 += 1
        else:
            ret.append((now, x1[p1][1]))
            now -= 1
            p0 += 1
            p1 += 1

    while p1 < len(x1) and now > 1:
        if not now > x1[p1][1]:
            return
        ret.append((now, x1[p1][1]))
        now -= 1
        p1 += 1
    if p0 != len(x0) or now != 1:
        return  # give up
    return ret


def correlation_1(x0, x1):
    p0, p1 = 0, 0
    while p0 < len(x0) and p1 < len(x1):
        if x1[p1][0].bit_length() > x0[p0][0].bit_length():
            diff = x1[p1][0].bit_length() - x0[p0][0].bit_length()
            while p0 < len(x0) and x1[p1][0] <= ((x0[p0][1]+1) << diff) - 1:
                p0 += 1
            if p0 == len(x0):
                continue
            low = (x0[p0][1] << diff)
            high = ((x0[p0][1]+1) << diff) - 1
            if low <= x1[p1][1] <= high:
                p0 += 1
                p1 += 1
                continue
            if 2 ** (x1[p1][0].bit_length()-1) <= x1[p1][1]:
                p1 += 1
                continue
            return False
        if x0[p0][1] != x1[p1][1]:
            if not x1[p1][0]-1 == x1[p1][1]:
                if x1[p1][1] >= x0[p0][0]:
                    p1 += 1
                    continue
                return False
            else:
                p1 += 1
        else:
            p0 += 1
            p1 += 1
    assert p0 == len(x0)
    return True


# ============================= for test =============================

# def randbelow_with_getrandbits(n):
#     "Return a random int in the range [0,n).  Raises ValueError if n==0."

#     k = n.bit_length()  # don't use (n-1) here because n can be 1
#     r = random.getrandbits(k)  # 0 <= r < 2**k
#     while r >= n:
#         r = random.getrandbits(k)
#     return r

# x0 = [(47, 30), (46, 34), (45, 3), (44, 27), (43, 27), (42, 29), (41, 23), (40, 11), (39, 3), (38, 2), (37, 24), (36, 32), (35, 2), (34, 11), (33, 9), (32, 9), (31, 8), (30, 6), (29, 22), (28, 17), (27, 26), (26, 7), (25, 19), (24, 5), (23, 2), (22, 21), (21, 7), (20, 7), (19, 8), (18, 17), (17, 16), (16, 7), (15, 0), (14, 10), (13, 10), (12, 5), (11, 5), (10, 1), (9, 6), (8, 2), (7, 4), (6, 2), (5, 4), (4, 2), (3, 1), (2, 0)]
# x1 = [(48, 30), (47, 34), (46, 3), (45, 27), (44, 27), (43, 29), (42, 23), (41, 11), (40, 3), (39, 2), (38, 24), (37, 32), (36, 2), (35, 11), (34, 9), (33, 9), (32, 17), (31, 6), (30, 22), (29, 17), (28, 26), (27, 7), (26, 19), (25, 5), (24, 2), (23, 21), (22, 7), (21, 7), (20, 8), (19, 17), (18, 16), (17, 7), (16, 1), (15, 10), (14, 10), (13, 5), (12, 5), (11, 1), (10, 6), (9, 2), (8, 5), (7, 5), (6, 4), (5, 2), (4, 3), (3, 0), (2, 1)]
# x2 = [(49, 30), (48, 34), (47, 3), (46, 27), (45, 27), (44, 29), (43, 23), (42, 11), (41, 3), (40, 2), (39, 24), (38, 32), (37, 2), (36, 11), (35, 9), (34, 9), (33, 17), (32, 13), (31, 22), (30, 17), (29, 26), (28, 7), (27, 19), (26, 5), (25, 2), (24, 21), (23, 7), (22, 7), (21, 8), (20, 17), (19, 16), (18, 7), (17, 1), (16, 10), (15, 5), (14, 1), (13, 6), (12, 2), (11, 8), (10, 5), (9, 8), (8, 5), (7, 3), (6, 1), (5, 4), (4, 3), (3, 1), (2, 1)]
# assert correlation_2(x0, x2) == x1

# while True:
#     seed = os.urandom(64)
#     random.seed(seed)
#     x0 = []
#     for i in reversed(range(1, 47)):
#         x0.append((i+1, randbelow_with_getrandbits(i+1)))
#     random.seed(seed)
#     x1 = []
#     for i in reversed(range(1, 48)):
#         x1.append((i+1, randbelow_with_getrandbits(i+1)))
#     random.seed(seed)
#     x2 = []
#     for i in reversed(range(1, 49)):
#         x2.append((i+1, randbelow_with_getrandbits(i+1)))
#     print(f'x0 = {x0}')
#     print(f'x1 = {x1}')
#     print(f'x2 = {x2}')
#     assert correlation_2(x0, x2) == x1

# ====================================================================


def get_shuffle_from_seq(seq, r=None):
    if r is None:
        r = list(range(seq[0][0]))
    else:
        r = copy.deepcopy(r)
    for x in seq:
        r[x[0]-1], r[x[1]] = r[x[1]], r[x[0]-1]
    return r


def recover_shuffle_from_seq(r: bytes, seq):
    r = bytearray(r)
    for x in seq[::-1]:
        r[x[0]-1], r[x[1]] = r[x[1]], r[x[0]-1]
    return bytes(r)


def guess_shuffle_middle(length: int, token: bytes):
    query_seqs_0 = crack_shuffle(length-1, token)
    query_seqs_1 = crack_shuffle(length+1, token)

    query_seqs = []
    for x0 in query_seqs_0:
        for x1 in query_seqs_1:
            ret = correlation_2(x0, x1)
            if ret is not None:
                query_seqs.append(ret)
    # assert len(query_seqs)
    for i in range(len(query_seqs)):
        log.info(
            f'Possible shuffle {i}: {get_shuffle_from_seq(query_seqs[i])}')
    return query_seqs


def guess_shuffle(length: int, token: bytes):
    query_seqs_0 = crack_shuffle(length-1, token)
    query_seqs_1 = crack_shuffle(length, token)

    query_seqs = []
    for x1 in query_seqs_1:
        for x0 in query_seqs_0:
            if correlation_1(x0, x1):
                query_seqs.append(x1)
                break
    # assert len(query_seqs)
    for i in range(len(query_seqs)):
        log.info(
            f'Possible shuffle {i}: {get_shuffle_from_seq(query_seqs[i])}')
    update_datebase((length, token), query_seqs)
    return query_seqs


def get_msg_pair(msg_length: int, xor_token: bytes, shuffle_token: bytes, seq):
    msg = bytearray(xor_token.rjust(msg_length+4, b'\x00'))
    idx = check_shuffle(bytes(get_shuffle_from_seq(seq, msg)), shuffle_token)
    progress = log.progress(f'Create legal ciphertext')
    progress.status(f'{idx}/{msg_length}')
    while idx < msg_length:
        msg[idx] = os.urandom(1)[0]
        idx = check_shuffle(
            bytes(get_shuffle_from_seq(seq, msg)), shuffle_token)
        progress.status(f'{idx}/{msg_length}')
    progress.success()
    msg_dec = decrypt(bytes(get_shuffle_from_seq(seq, msg)) + shuffle_token)
    log.debug(f'Cipher text: {msg}')
    log.debug(f'Original text: {msg_dec}')
    return msg, msg_dec


def crack_xor(length: int, xor_token: bytes, shuffle_token: bytes, seq):
    progress = log.progress('crack_xor')
    msg, _ = get_msg_pair(length, xor_token, shuffle_token, seq)
    ret = []
    progress.status(f'{len(ret)}/{length} 0/256 {ret}')
    for i in range(length):
        _c = msg[i]
        r = [None] * (2**8)
        for o in range(2**8):
            progress.status(f'{len(ret)}/{length} {o}/256 {ret}')
            msg[i] = o
            try:
                r[o] = ord(
                    decrypt(bytes(get_shuffle_from_seq(seq, msg)) + shuffle_token)[i])
            except InvalidChar:
                continue
        msg[i] = _c

        mapping = [None] * 8
        for j in range(8):
            for o in range(2**8):
                if o & (1 << j) == 0 and r[o] is not None and r[o | (1 << j)] is not None:
                    c = r[o] ^ r[o | (1 << j)]
                    assert 2 ** (c.bit_length() - 1) == c
                    mapping[j] = c.bit_length() - 1
                    break
            if mapping[j] is None:
                mapping[j] = 7

        o = 0
        while r[o] is None:
            o += 1
        o_bits = bin(o)[2:].zfill(8)[::-1]
        v_bits = ''
        for j in range(8):
            v_bits += o_bits[mapping.index(j)]
        v = int(v_bits[::-1], 2)
        ret.append(r[o] ^ v)
        progress.status(f'{len(ret)}/{length} 256/256 {ret}')
    progress.success()
    return ret


def test_xor(length: int, xor_token: bytes, shuffle_token: bytes, seq, rand_num):
    progress = log.progress('test_xor')
    msg, _ = get_msg_pair(length, xor_token, shuffle_token, seq)
    progress.status(f'0/4 0/256')
    for i in range(4):
        _c = msg[i]
        r = [None] * (2**8)
        for o in range(2**8):
            progress.status(f'{i}/4 {o}/256')
            msg[i] = o
            try:
                r[o] = ord(
                    decrypt(bytes(get_shuffle_from_seq(seq, msg)) + shuffle_token)[i])
            except InvalidChar:
                continue
        msg[i] = _c

        mapping = [None] * 8
        for j in range(8):
            for o in range(2**8):
                if o & (1 << j) == 0 and r[o] is not None and r[o | (1 << j)] is not None:
                    c = r[o] ^ r[o | (1 << j)]
                    assert 2 ** (c.bit_length() - 1) == c
                    mapping[j] = c.bit_length() - 1
                    break
            if mapping[j] is None:
                mapping[j] = 7

        o = 0
        while r[o] is None:
            o += 1
        o_bits = bin(o)[2:].zfill(8)[::-1]
        v_bits = ''
        for j in range(8):
            v_bits += o_bits[mapping.index(j)]
        v = int(v_bits[::-1], 2)
        if r[o] ^ v != rand_num[i]:
            progress.failure()
            return False
        progress.status(f'{i+1}/4 256/256')

    progress.success()
    return True


def test_bits_shuffle(length: int, xor_token: bytes, shuffle_token: bytes, seq, flag_enc: bytes, rand_num):
    progress = log.progress('test_bits_shuffle')
    msg, _ = get_msg_pair(length, xor_token, shuffle_token, seq)
    ret = [None]
    known = bytearray(b'TQLCTF{')
    length = len(flag_enc)
    progress.status(f'{len(ret)}/{length} 0/256 {known} {ret}')
    for i in range(length-1):
        _c = msg[i]
        r = [None] * (2**8)
        for o in range(2**8):
            progress.status(f'{len(ret)}/{length} {o}/256 {known} {ret}')
            msg[i] = o
            try:
                r[o] = ord(
                    decrypt(bytes(get_shuffle_from_seq(seq, msg)) + shuffle_token)[i])
            except InvalidChar:
                continue
        msg[i] = _c

        mapping = [None] * 8
        for j in range(8):
            for o in range(2**8):
                if o & (1 << j) == 0 and r[o] is not None and r[o | (1 << j)] is not None:
                    c = r[o] ^ r[o | (1 << j)]
                    assert 2 ** (c.bit_length() - 1) == c
                    mapping[j] = c.bit_length() - 1
                    break
            if mapping[j] is None:
                mapping[j] = 7

        ret.append(copy.deepcopy(mapping))
        progress.status(f'{len(ret)}/{length} 256/256 {known} {ret}')

        bits = list(bin(flag_enc[i+1])[2:].zfill(8))[::-1]
        for j in range(8):
            _t = mapping.index(j)
            mapping[j], mapping[_t] = mapping[_t], mapping[j]
            bits[j], bits[_t] = bits[_t], bits[j]
        value = int(''.join(bits[::-1]), 2) ^ rand_num[i+1]
        if i+1 < len(known):
            if known[i+1] != value:
                progress.failure(f'{ret} {known} {i, value, chr(value)}')
                return False
        else:
            known.append(value)

    progress.success(f'{ret} {known}')
    return True


def guess_shuffle_xor(length: int, xor_token: bytes, shuffle_token: bytes, rand_num: bytes):
    query_seqs = crack_shuffle(length, shuffle_token)

    if len(query_seqs) == 1:
        return query_seqs[0]

    progress = log.progress('guess_shuffle_xor')
    for idx, seq in enumerate(query_seqs):
        progress.status(f'{idx}/{len(query_seqs)}')
        if test_xor(length-4, xor_token, shuffle_token, seq, rand_num):
            progress.success()
            update_datebase((length, shuffle_token), [seq])
            return seq
    progress.failure()
    raise RuntimeError


if __name__ == '__main__':
    while True:
        flag_query_seqs = guess_shuffle_middle(FLAG_TOKEN_LEN, flag_token_1)
        log.info(f'len(flag_query_seqs): {len(flag_query_seqs)}')
        if len(flag_query_seqs) == 1:
            break
        rebuild()

    flag_seq = flag_query_seqs[0]

    flag_enc2 = recover_shuffle_from_seq(flag_enc, flag_seq)
    flag_enc2, flag_token_0 = flag_enc2[:-4], flag_enc2[-4:]

    diy_token = os.urandom(4)
    progress = log.progress(
        'finding a shuffle token where there is only one possible query_seqs')
    progress.status(diy_token.hex())
    while True:
        diy_query_seqs = guess_shuffle(FLAG_TOKEN_LEN+1, diy_token)
        if len(diy_query_seqs) == 1:
            break
        diy_token = os.urandom(4)
        progress.status(diy_token.hex())
    progress.success(diy_token.hex())
    diy_seq = diy_query_seqs[0]

    rand_num = crack_xor(FLAG_LEN+1, flag_token_0, diy_token, diy_seq)
    log.info(f'rand_num: {rand_num}')

    N = FLAG_TOKEN_LEN+7*4-3
    while N <= FLAG_TOKEN_LEN+14*4-3:
        seq = guess_shuffle_xor(N, flag_token_0, diy_token, rand_num)
        if test_bits_shuffle(N-4, flag_token_0, diy_token, seq, flag_enc2, rand_num):
            break
        N += 4
