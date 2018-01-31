# coding: utf-8

import tensorflow as tf

import cnn

IMAGE_HEIGHT = 30
IMAGE_WIDTH = 104
MAX_CAPTCHA = 4
CHAR_SET_LEN = 10 + 26  # 数字加英文不区分大小写

image = []  # 输入图

output = crack_captcha_cnn()
saver = tf.train.Saver()
with tf.Session() as sess:
    saver.restore(sess, tf.train.latest_checkpoint('.'))

    predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
    text_list = sess.run(predict, feed_dict{X:[image], keep_prob: 1})
    text = text_list[0].tolist()

    print text
