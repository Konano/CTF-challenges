#!/usr/bin/python3
import os
import random
from flag import award

random.seed(os.urandom(64))

with open('allowed_guesses.txt', 'r') as f:
    allowed_guesses = set([x.strip() for x in f.readlines()])

with open('valid_words.txt', 'r') as f:
    valid_words = [x.strip() for x in f.readlines()]


MAX_LEVEL = 512
GREEN = '\033[42m  \033[0m'
YELLOW = '\033[43m  \033[0m'
WHITE = '\033[47m  \033[0m'

def get_challenge():
    # id = random.getrandbits(32)
    # answer = valid_words[id % len(valid_words)]
    # return hex(id)[2:].zfill(8), answer

    # To prevent the disclosure of answer
    id = random.randrange(len(valid_words) * (2 ** 20))
    answer = valid_words[id % len(valid_words)]
    id = (id // len(valid_words)) ^ (id % len(valid_words))
    return hex(id)[2:].zfill(5), answer

def check(answer, guess):
    answer_chars = []
    for i in range(5):
        if guess[i] != answer[i]:
            answer_chars.append(answer[i])
    result = []
    for i in range(5):
        if guess[i] == answer[i]:
            result.append(GREEN)
        elif guess[i] in answer_chars:
            result.append(YELLOW)
            answer_chars.remove(guess[i])
        else:
            result.append(WHITE)
    return ' '.join(result)

def game(limit):
    round = 0
    while round < MAX_LEVEL:
        round += 1
        id, answer = get_challenge()
        print(f'Round {round}: #{id}')
        correct = False
        for _ in range(limit):
            while True:
                guess = input('> ')
                if len(guess) == 5 and guess in allowed_guesses:
                    break
                print('Invalid guess')
            result = check(answer, guess)
            if result == ' '.join([GREEN] * 5):
                print(f'Correct! {result}')
                correct = True
                break
            else:
                print(f'Wrong!   {result}')
        if not correct:
            print('You failed...')
            return round - 1

    return MAX_LEVEL


def choose_mode():
    print('Choose gamemode:')
    print('0: Easy mode')
    print('1: Normal mode')
    print('2: Hard mode')
    print('3: Insane mode')
    # print('4: Expert mode')
    # print('-1: Osu! mode')
    mode = int(input('> '))
    assert 0 <= mode <= 3
    return mode

if __name__ == '__main__':
    print('Guess the WORDLE in a few tries.')
    print('Each guess must be a valid 5 letter word.')
    print('After each guess, the color of the tiles will change to show how close your guess was to the word.')

    while True:
        mode = choose_mode()
        if mode == 0:
            limit = 999999999
        else:
            limit = 7 - mode
        final_level = game(limit)
        if final_level < MAX_LEVEL:
            pass
        else:
            print('You are the Master of WORDLE!')
        flag = award(mode, final_level)
        print(f'Here is you award: {flag}')
