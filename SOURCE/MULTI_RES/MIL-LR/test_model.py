#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 15:04:36 2019

@author: ghosh128
"""

import sys
sys.path.append("../../")
import os
import config
import numpy as np
import tensorflow as tf
from sklearn.metrics import f1_score
import matplotlib.pyplot as plt
tf.set_random_seed(1)
# %%
print("LOAD DATA")
test_data_fine = np.load(os.path.join(config.NUMPY_DIR, "sentinel_test_data.npy"))
test_data_coarse = np.load(os.path.join(config.NUMPY_DIR, "landsat_test_data.npy"))
num_features_fine = 12
num_features_coarse = 11
# %%
print("BUILD MODEL")
tf.reset_default_graph()
with tf.name_scope('data'):
    X_fine = tf.placeholder(tf.float32, [None, num_features_fine], name="fine_res_inputs")
    Y_fine = tf.placeholder(tf.float32, [None, 1], name="fine_res_labels")
    X_coarse = tf.placeholder(tf.float32, [None, num_features_coarse], name="corase_res_inputs")
    Y_coarse = tf.placeholder(tf.float32, [None, 1], name="coarse_res_labels")
    X_fine_consistency= tf.placeholder(tf.float32, [9*config.batch_consistency, num_features_fine], name="fine_res_consistency_inputs")
    X_coarse_consistency = tf.placeholder(tf.float32, [config.batch_consistency, num_features_coarse], name="coarse_res_consistency_inputs")

with tf.variable_scope("Variables", reuse=tf.AUTO_REUSE):
    W_fine = tf.get_variable("Weights_fine", [num_features_fine, 1], initializer=tf.contrib.layers.xavier_initializer())
    b_fine = tf.get_variable("Biases_fine", [1], initializer=tf.zeros_initializer())
    W_coarse = tf.get_variable("Weights_coarse", [num_features_coarse, 1], initializer=tf.contrib.layers.xavier_initializer())
    b_coarse = tf.get_variable("Biases_coarse", [1], initializer=tf.zeros_initializer())

Z_fine = tf.matmul(X_fine, W_fine, name="multiply_weights")
Z_fine = tf.add(Z_fine, b_fine, name="add_bias")
Z_fine = tf.nn.sigmoid(Z_fine)

Z_coarse = tf.matmul(X_coarse, W_coarse, name="multiply_weights")
Z_coarse = tf.add(Z_coarse, b_coarse, name="add_bias")
Z_coarse = tf.nn.sigmoid(Z_coarse)
#%%
print("TEST MODEL")
saver = tf.train.Saver()
with tf.Session() as sess:
    saver.restore(sess, os.path.join(config.MODEL_DIR, "MULTI_RES", "MIL-LR", "model.ckpt"))
    data_fine = test_data_fine[:,:num_features_fine]
    data_coarse = test_data_coarse[:,:num_features_coarse]
    feed_dict = {X_fine: data_fine, X_coarse: data_coarse}
    preds_fine, preds_coarse = sess.run([Z_fine, Z_coarse], feed_dict=feed_dict)

pred_labels_fine = np.zeros(preds_fine.shape)
pred_labels_fine[preds_fine > 0.5] = 1
pred_labels_fine[preds_fine < 0.5] = 0
labels_fine = np.reshape(test_data_fine[:, -1], [-1, 1])

pred_labels_coarse = np.zeros(preds_coarse.shape)
pred_labels_coarse[preds_coarse > 0.5] = 1
pred_labels_coarse[preds_coarse < 0.5] = 0
labels_coarse = np.reshape(test_data_coarse[:, -1], [-1, 1])

print("Accuracy_fine:", len(np.where([pred_labels_fine == labels_fine])[1])/int(len(labels_fine)), "Accuracy_coarse:", len(np.where([pred_labels_coarse == labels_coarse])[1])/int(len(labels_coarse)))
print("f1_score_fine:", f1_score(labels_fine, pred_labels_fine), "f1_score_coarse:", f1_score(labels_coarse, pred_labels_coarse))
plt.hist(preds_fine[labels_fine==0], color="red")
plt.hist(preds_fine[labels_fine==1], color="green")
plt.show()
plt.hist(preds_coarse[labels_coarse==0], color="red")
plt.hist(preds_coarse[labels_coarse==1], color="green")
plt.show()
