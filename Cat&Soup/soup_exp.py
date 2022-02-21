from PIL import Image

im = Image.open('soup.png')
palette = im.palette.getdata()[1]
width = im.size[0]
height = im.size[1]

color = []
Yid = []
for i in range(256):
    r, g, b = palette[3*i], palette[3*i+1], palette[3*i+2]
    color.append((r, g, b))
    Y = 0.299 * r + 0.587 * g + 0.114 * b
    Yid.append((Y, i))
assert len(set([x[0] for x in Yid])) == 256

Yid = [x[1] for x in sorted(Yid)]
Xid = {}
for i in range(256):
    Xid[i] = Yid.index(i)

flag = []

for x in range(width):
    for y in range(height):
        id = im.getpixel((x, y))
        id = Xid[id]
        flag.append(str(id & 1))

now = 1
while flag[now:] != flag[:-now]:
    now += 1

flag = ''.join([chr(int(''.join(flag[i:i+7]), 2)) for i in range(0, now, 7)])
print(flag)
