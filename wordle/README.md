# wordle

## Description

What is the best strategy for wordle?

## Flag

`TQLCTF{th3_be5T_FIrS7_WORD_1s_CURr3ntly_s@lEt_3.42117~}`

## Writeup

本题需要选手在加强版 Wordle 游戏中连续 512 轮四次以内猜中词语才会获得最终的 flag。

首先需要明白一点，纯算法连续 512 轮四次之内猜测正确的可能性是近乎为 0 的（当然如果有师傅用纯算法的方法过了这题请联系我让我膜一下）

主要漏洞点出在 `get_challenge` 处：

```python
def get_challenge():
    # id = random.getrandbits(32)
    # answer = valid_words[id % len(valid_words)]
    # return hex(id)[2:].zfill(8), answer

    # To prevent the disclosure of answer
    id = random.randrange(len(valid_words) * (2 ** 20))
    answer = valid_words[id % len(valid_words)]
    id = (id // len(valid_words)) ^ (id % len(valid_words))
    return hex(id)[2:].zfill(5), answer
```

valid_words 大小为 $4090$，乘上 $2^{20}$ 约等于 $2^{32}$，而 randrange 的结果是可以通过正确答案以及每道题的 ID 逆推获得的。

让我们跟踪进去看看 random 内部的实现：

```python
    _randbelow = _randbelow_with_getrandbits
    
    def _randbelow_with_getrandbits(self, n):
        "Return a random int in the range [0,n).  Raises ValueError if n==0."

        getrandbits = self.getrandbits
        k = n.bit_length()  # don't use (n-1) here because n can be 1
        r = getrandbits(k)          # 0 <= r < 2**k
        while r >= n:
            r = getrandbits(k)
        return r

    def randrange(self, start, stop=None, step=1, _int=int):
        """Choose a random item from range(start, stop[, step]).

        This fixes the problem with randint() which includes the
        endpoint; in Python this is usually not what you want.

        """

        # This code is a bit messy to make it fast for the
        # common case while still doing adequate error checking.
        istart = _int(start)
        if istart != start:
            raise ValueError("non-integer arg 1 for randrange()")
        if stop is None:
            if istart > 0:
                return self._randbelow(istart)
            raise ValueError("empty range for randrange()")
        
        # ....
```

从这里可以看出，randrange 实际上就是在调用 getrandbits(32)，所以这里就可以套用 [Python random module cracker](https://github.com/tna0y/Python-random-module-cracker) 来预测答案！

总结一下：通过两轮 Easy Mode 获得前 624 道题的答案，结合 ID 反推 getrandbits(32) 的值并丢进 random-cracker 获得预测随机数的能力

注意到 $4090*2^{20}$ 离 $2^{32}$ 还有一定的差距，结合代码可知如果 getrandbits(32) 大于 $4060*2^{20}$，则该数将会被丢弃导致预测随机数失败。经过计算可知，成功率为 $\left(\frac{4090}{4096}\right)^{624}=0.4006237250$ ，十分可观。
