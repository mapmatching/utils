# coding: utf-8

import traceback

import os
import cv2
import numpy
from PIL import Image

from bitstring import BitArray, BitStream

from bk_tree import BKTree, Node
from sessions import star_session, spider_session


def hash_image(file_path):
    img = Image.open(file_path)
    img = img.resize((300, 300))
    img.thumbnail((8, 8), Image.ANTIALIAS)  # NOTE hash大小可调整，改变后需要重新计算星发所有封面hash值
    matrix = numpy.asarray(img.convert('L'))

    gray = 0
    for i in matrix:
        for j in i:
            gray += j
    gray /= 64
    hash_str = ''
    # gray_matrix = numpy.zeros((8, 8), dtype=int)
    for i in range(8):
        for j in range(8):
            hash_str += str(int(matrix[i][j] >= gray))
            # gray_matrix[i][j] = 255 if int(matrix[i][j] >= gray) else 0
    return hash_str

def get_index(p):
    def func(n):
        if n < 64:         
            return 0       
        if n < 128:        
            return 1       
        if n < 192:        
            return 2
        return 3
    return func(p[0])*16 + func(p[1])*4 + func(p[2]) 

def hist_image(file_path):
    img = Image.open(file_path)
    img = img.resize((50, 50)).convert('RGB')
    result = [0]*64
    array = numpy.asarray(img).reshape(-1, 3)
    for p in array:
        result[get_index(p)] += 1
    return result

def hamming_weight(a, b):
    return (a^b).count(True)

def vector_distance(a, b):
    s = 0
    l1 = l2 = 0
    for i in range(64):
        s += (a[i]-b[i])*(a[i]-b[i])
        l1 = a[i] * a[i]
        l2 = b[i] * b[i]
    return s

def vector_length(a):
    l = 0
    for i in range(64):
        l += a[i]*a[i]
    return l


class MatchError(Exception):
    def __init__(self, album):
        self.album=album


def init_bktree():
    bktree = BKTree()
    for i, album in enumerate(spider_session.execute('''select * from star_album''').fetchall()):
        if len(album._hash) == 64:
            bktree.insert(Node(BitArray('0b'+album._hash), data=dict(id=album.star_id, hist=album.hist)))
        if i % 10000 == 0:
            print i
    print 'init finishes'
    return bktree


detector = cv2.xfeatures2d.SIFT_create()
bf = cv2.BFMatcher()

def check_same_image(filepath1, filepath2):
    '''
        这个函数调的作用不大
    '''
    img1 = cv2.imread(filepath1, 0)
    img2 = cv2.imread(filepath2, 0)
    kp1, des1 = detector.detectAndCompute(img1, None)
    kp2, des2 = detector.detectAndCompute(img2, None)
    matches = bf.knnMatch(des1, des2, k=2)
    match_param = 0.6  # NOTE 这个0.6可以调
    good = []
    for m, n in matches:
        if m.distance < match_param*n.distance:
            good.append([m])
    print len(good), len(kp1), len(kp2)
    img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None,flags=2)
    cv2.imwrite("shift_result.png", img3)
    if len(good) < len(kp1) * 0.2 and len(good) < len(kp2) * 0.2:  # NOTE 这个0.2可以调
        return False
    return True

def find_most_similar(file_path, potential_list):
    img_target = cv2.imread(target, 0)
    img_list = [cv2.imread(p, 0) for p in potential_list]
    kp, des = detector.detectAndCompute(img_target, None)
    min_index = -1
    min_good = 999999999
    for i, img in enumerate(img_list):
        img = cv2.resize(img, (500, 500), interpolation=cv2.INTER_CUBIC)
        tkp, tdes = detector.detectAndCompute(img, None)
        matches = bf.knnMatch(des, tdes, k=2)
        match_param = 0.6
        good = []
        for m, n in matches:
            if m.distance < match_param*n.distance:
                good.append([m])
        if min_good > len(good):
            min_index = i
            min_good = len(good)

    return min_good

def get_star_album_cover_path(star_id):
    star_album = star_session.execute('''select * from kanjian_ddex_album where id=:id''', dict(id=star_id)).fetchone()
    if star_album.cover_path:
        return os.path.join('/data/public/ftphome/', star_album.cover_path)
    return ''
