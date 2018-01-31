# coding: utf8
import os

from PIL import Image
import numpy

width = 104
height = 30


def check_black_point(i, j, arr):
    '''检查是否黑点'''
    if arr[i][j] == (0, 0, 0):
        return True
    return False


def check_color_block(i, j, arr):
    '''检查是否纯色块'''
    if arr[i][j] == (255, 255, 255):
        return False
    a = [-2, -1, 0, 1, 2]
    b = [(a[ii], a[jj]) for ii in range(5) for jj in range(5)]
    count = 0
    for (ni, nj) in b:
        if arr[i+ni][j+nj] != arr[i][j]:
            count += 1
    if count > 5:
        return False
    return True


def replace_color_block(color, arr):
    for i in range(width):
        for j in range(height):
            if arr[i][j] == color:
                arr[i][j] = (255, 255, 255)
    return arr


def _pre(arr):
    for i in range(30):
        arr[0][i] = (255, 255, 255)
        arr[1][i] = (255, 255, 255)
        arr[103][i] = (255, 255, 255)
        arr[102][i] = (255, 255, 255)
    for i in range(104):
        arr[i][0] =  (255, 255, 255)
        arr[i][1] =  (255, 255, 255)
        arr[i][29] =  (255, 255, 255)
        arr[i][28] =  (255, 255, 255)
    for i in range(2, width-2):
        for j in range(2, height-2):
            if arr[i][j] != (255, 255, 255):
                if check_black_point(i, j, arr):
                    arr[i][j] = (255, 255, 255)
                if check_color_block(i, j, arr):
                    arr = replace_color_block(arr[i][j], arr)
    return arr


def save_as_png(arr):
    new_img = Image.new('RGB', (len(arr), len(arr[0])))
    a = []
    for i in range(len(arr[0])):
        a += [arr[j][i] for j in range(len(arr))]
    new_img.putdata(a)
    new_img.save('out.png')


def pre(filename):
    f = Image.open(filename).convert('RGB')
    arr = numpy.array(f)
    arr = [[tuple(arr[i][j]) for i in range(height)] for j in range(width)]
    arr = _pre(arr)
    return arr


if __name__ == '__main__':
    for f in os.listdir('data'):
        f = Image.open(os.path.join('data', f)).convert('RGB')
        arr = numpy.array(f)
        arr = [[tuple(arr[i][j]) for i in range(height)] for j in range(width)]
        arr = _pre(arr)

        r = []
        for i in range(width):  # 列
            min_row = 105
            max_row = -1
            for j in range(height):  # 行
                if tuple(arr[i][j]) != (255, 255, 255):
                    min_row = min(min_row, j)
                    max_row = max(max_row, j)
            if (max_row - min_row) < 5:
                r.append('w')
            else:
                r.append('b')
        print ''.join(r)
        # save_as_png(arr)
