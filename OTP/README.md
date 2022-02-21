# OTP

## Description

Secure one-time password encryption program

## Flag

`TQLCTF{eee67011-f2a0-4f5f-ae48-1de28c769739}`

## Writeup

这题实现了一种略显复杂的一次性密码加密算法。

这题的难点还挺多的，特别在加入了 DangerousBehavior 的监测机制和 secret 之后。

加密过程：shuffle(xor_bits_shuffle(M, Rand(len(M), f1+s1))+f1, f2+s2)+f2

### Step 1

拿到密文，很容易知道 shuffle 所用的 token 是什么，但由于有 secret，并不能反推出 shuffle 的打乱规则，继而更难推导后面 xor 所用的 token。

注意到题目解密时如果发现有非法字符，会返回一个带有下标的提示，可以利用这个爆破出明文在经过 shuffle 后的位置，这样可以将 shuffle 的可能性减少到 24 种（并不能知道 token 经过 shuffle 后的顺序）

注意到 shuffle 和数组长度是有关的，所以在加入了 DangerousBehavior 的监测机制之后，想要得到和 flag 同长度情况下的 shuffle 情况是不可能的，这时候只能退而求其次求得 flag_length±1 时同 token 的 shuffle 情况，然后推导在 flag_length 不变的情况下 shuffle 的情况。

如何从两个 ±1 的 shuffle 情况推导出中间的 shuffle 情况？通过研究源码可以知道 random.shuffle 是通过 n-1 次两两交换来打乱序列，交换对象由 random.getbelow 决定，所以某些情况下相邻长度的 shuffle 情况是相似的。（这步建议可以用人脑或者程序研究研究）

那么此时我们知道了 shuffle(?, f2+s2) 的打乱规则，获得了 xor_bits_shuffle(M, Rand(len(M), f1+s1)) 和 f1 的信息。

### Step 2

根据源码可知，xor_bits_shuffle 是指对字符串做 xor 后再一个个字节进行 bits_shuffle，且中间不重置 random.seed。

首先因为 DangerousBehavior 的监测机制，我们需要随机一个 token 替代 f2 用来做 shuffle，并用第一步的方法获得特定长度下 shuffle 的结果。

xor 的结果只和 f1 有关，所以此时也可以通过爆破获得 xor 的 Rand(len(M), f1+s1)，进而得到 bits_shuffle 的结果。

但是，注意到这里的 bits_shuffle 和明文长度有关（中间不重置 random.seed），而 DangerousBehavior 的监测机制又阻止我们在只改变 shuffle_token 的情况下爆破 bits_shuffle，看似又是一个无解的情况。

还记得之前说过的 random.shuffle 的实现吗？random.getbelow 的实现也是基于 getrandbits，再深挖 getrandbits 的实现我们可以知道，在未来的某一个长度下，bits_shuffle 的情况会重复出现！所以只需要爆破后续某些特定长度下的 bits_shuffle 情况，然后结合 xor 尝试破解 flag 的密文。如果前缀匹配上的话那么大概率就是正解了。

### 后记

这题的 DangerousBehavior 判断放得太后了，导致所有在比赛场上做出这道题的人都利用了 valid_pos 的报错而绕过了 DangerousBehavior，从而出现了更加简单的非预期解法。虽然即便是这样解出这道题的队伍也只有 4 个，但还是略显遗憾，没能让大家真的去预测 shuffle 后的结果……放在 GitHub 上的[题目代码](https://github.com/Konano/CTF-challenges/blob/master/OTP/main.py)已经修复了该处 Bug，有兴趣的可以自己试试看。
