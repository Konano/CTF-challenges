# Nanomaze

## Description

The ultimate invisible puzzle challenge.

## Flag

`TQLCTF{ReV0m4Ze_1EGEnD@rY_gR@nDM4St3R}`

## Writeup

这是一道纯黑箱题目，考察选手们黑灯瞎火走迷宫的能力（大雾）

题目背景是 Revomaze，一款出自英格兰的 Puzzle 系列。题目基本上还原了 Puzzle 的地图和声音，让选手们能够身临其境免费游玩 Puzzle！选手在题目中只能通过 wasd 上下移动，且能听到咔哒一声（指 `[click]`）。Puzzle 的具体情况可以看 [GM 的秘密基地的游玩视频](https://www.bilibili.com/video/av720802187)，本题正是复刻了 Revomaze Green 的迷宫。

最后为了加大难度，本题还抛弃了单位移动距离，改成了随机实数距离。

![地图](https://oss.nan.pub/imgs/image-20220221214650722.png)

黑箱交互的题怎么做呢？首先通过乱按发现 wasd 这四种输入能够触发有效的回显，并且知道了随机移动距离这个特点；然后通过左右走动发现可以无限往左走，猜测是一个循环地图；触发了 `[click]` 之后往回走发现撞墙了，猜测 `[click]` 指的是单向门……

当然你也可以在知道这是个循环地图后无视 `[click]` 直接遍历全图，这样也可以到达终点。
