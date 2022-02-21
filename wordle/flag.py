MAX_LEVEL = 512

# flag = 'TQLCTF{the_best_first_word_is_currently_salet_3.42117~}'
flag = 'TQLCTF{th3_be5T_FIrS7_WORD_1s_CURr3ntly_s@lEt_3.42117~}'
flag_shuffle = 'F7_7__S324rsT3_T}L3_CUt1R~s_tn@WITO_eCbQ{rRh1lty1EDlF5.'


def cover(s, level):
    show_len = int(level * len(s) / MAX_LEVEL)
    return s[:show_len] + '*' * (len(s) - show_len)


def award(mode, level):
    if mode == 0:
        return 'NULL'
    elif mode == 1:
        # 1 url + reverse + base64
        return cover('UWNYZ1c5dzR3UWQ9dj9oY3Rhdy9tb2MuZWJ1dHVveS53d3cvLzpzcHR0aA==', level)
    elif mode == 2:
        # 2 real flag + shuffle
        return cover(flag_shuffle, level)
    elif mode == 3:
        # 3 real flag
        return cover(flag, level)
