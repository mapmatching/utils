# coding: utf-8

import os
from PIL import Image
import tensorflow as tf

import pre
import validation

tf.logging.set_verbosity(tf.logging.INFO)

IMAGE_HEIGHT = 200
IMAGE_WIDTH = 64
MAX_CAPTCHA = 4
CHAR_SET_LEN = 26  # 数字加英文不区分大小写

X = tf.placeholder(tf.float32, [None, IMAGE_WIDTH, IMAGE_HEIGHT, 1], name="X")  # 输入
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA*CHAR_SET_LEN], name="Y")  # 输出
# Y = tf.placeholder(tf.float32, [None, CHAR_SET_LEN])  # 输出
keep_prob = tf.placeholder(tf.float32) # dropout


file_list = []
for f in os.listdir('data2'):
    if f.endswith('png'):
        file_list.append('data/'+f)

def text_to_y(text):
    # text = text.lower()
    a = [0 for i in range(MAX_CAPTCHA*CHAR_SET_LEN)]
    for i, t in enumerate(text):
        a[i*CHAR_SET_LEN + (ord(t)-ord('A'))] = 1
    if text[0] != y_to_text(a):
        print text, y_to_text(a)
        raise
    return a

def arr_to_x(arr):
    tmp = []
    for i in range(IMAGE_WIDTH):
        for j in range(IMAGE_HEIGHT):
            tmp.append(255 - (0.2989*arr[i][j][0] + 0.5870*arr[i][j][1] + 0.1140*arr[i][j][2]))
    return tmp


def y_to_text(y):
    r = ''
    step = CHAR_SET_LEN
    for i in range(1):
        m = -9999999
        mi = 0
        for index, j in enumerate(y[i*step: (i+1)*step]):
            if j > m:
                mi = index
                m = j
        r += chr(mi+ord('A'))
    return r

def get_next_batch(size=1):
    # import random
    # fl = random.sample(file_list, size)
    # fl = file_list[:1]
    xx = []
    yy = []
    for i in range(size):
        arr, cl = validation.Validation.new_validation_code()
        xx.append(arr_to_x(arr))
        yy.append(text_to_y(cl))
    return xx, yy

def cnn(w_alpha=0.01, b_alpha=0.1):
    x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])

    # 3 conv layer
    w_c1 = tf.Variable(w_alpha*tf.random_normal([3, 3, 1, 32]))
    b_c1 = tf.Variable(b_alpha*tf.random_normal([32]))
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))
    conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv1 = tf.nn.dropout(conv1, keep_prob)

    w_c2 = tf.Variable(w_alpha*tf.random_normal([3, 3, 32, 64]))
    b_c2 = tf.Variable(b_alpha*tf.random_normal([64]))
    conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'), b_c2))
    conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv2 = tf.nn.dropout(conv2, keep_prob)

    w_c3 = tf.Variable(w_alpha*tf.random_normal([3, 3, 64, 64]))
    b_c3 = tf.Variable(b_alpha*tf.random_normal([64]))
    conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))
    conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv3 = tf.nn.dropout(conv3, keep_prob)

    # Fully connected layer
    w_d = tf.Variable(w_alpha*tf.random_normal([50*16*64, 1024]))
    b_d = tf.Variable(b_alpha*tf.random_normal([1024]))
    dense = tf.reshape(conv3, [-1, w_d.get_shape().as_list()[0]])
    # dense = tf.reshape(conv2, [-1, w_d.get_shape().as_list()[0]])
    dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))
    dense = tf.nn.dropout(dense, keep_prob)

    w_out = tf.Variable(w_alpha*tf.random_normal([1024, MAX_CAPTCHA*CHAR_SET_LEN]))
    b_out = tf.Variable(b_alpha*tf.random_normal([MAX_CAPTCHA*CHAR_SET_LEN]))
    # w_out = tf.Variable(w_alpha*tf.random_normal([1024, CHAR_SET_LEN]))
    # b_out = tf.Variable(b_alpha*tf.random_normal([CHAR_SET_LEN]))
    out = tf.add(tf.matmul(dense, w_out), b_out)
    out = tf.nn.softmax(out)
    return out


# def train():
if __name__ == '__main__':
    output = cnn()
    # loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(output, Y))
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)
    # predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
    predict = tf.reshape(output, [-1, 1, CHAR_SET_LEN])
    max_idx_p = tf.argmax(predict, 2)
    # max_idx_l = tf.argmax(tf.reshape(Y, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
    max_idx_l = tf.argmax(tf.reshape(Y, [-1, 1, CHAR_SET_LEN]), 2)
    correct_pred = tf.equal(max_idx_p, max_idx_l)
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

    saver = tf.train.Saver()
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    step = 1
    while True:
        batch_x, batch_y = get_next_batch(64)
        _, loss_ = sess.run([optimizer, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
        print(step, loss_)

        if step % 10 == 0:
            batch_x_test, batch_y_test = get_next_batch(10)
            # out = sess.run(output, feed_dict={X: batch_x_test, keep_prob: 1})
            # for i, y in enumerate(batch_y_test):
            #     print y_to_text(out[i]), y_to_text(y)
            acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
            print('------------------', step, acc)
            # 如果准确率大于50%,保存模型,完成训练
            if acc > 0.6:
                saver.save(sess, "crack_capcha.model", global_step=step)
        step += 1


# train()

# output = crack_captcha_cnn()
# saver = tf.train.Saver()
# with tf.Session() as sess:
#     saver.restore(sess, tf.train.latest_checkpoint('.'))
# 
#     predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
#     text_list = sess.run(predict, feed_dict{X:[image], keep_prob: 1})
#     text = text_list[0].tolist()
# 
#     print text
