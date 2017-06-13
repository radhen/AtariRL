## CNN1D.py
##
## A simple 1D Convolution Neural Network classifier model.

import tensorflow as tf
import numpy as np
from parts import *


DEEPMIND_LAYERS = [Convolutional((8,8), 32, name='conv1', stride=4),
                   ReLU(name='relu1'),
                   Convolutional((4,4), 64, name='conv2', stride=2),
                   ReLU(name='relu2'),
                   Convolutional((3,3), 64, name='conv3', stride=1),
                   ReLU(name='relu3'),
                   Flatten(name='flatten'),
                   FullConnection(512, name='full1'),
                   ReLU(name='relu4'),
                   FullConnection(4, name='full2'),
                   Linear(name='linear')
            ]

class DeepQNetwork(object):

   def __init__(self, frame_shape, hidden_layers, num_actions, **kwargs):
      """
      Build a deep convolutional neural network network

      frame_shape    - shape of the input frame: (width x height x num_channels)
      hidden_layers  - A list of hidden layers, which take the form of a tuple, which depends
                       on the type (first element of the tuple)
      num_targets    - the number of actions which can be performed
      """

      # Input and target placeholders
      self.input = tf.placeholder(tf.float32, shape=(None,) + tuple(frame_shape))
      self.target = tf.placeholder(tf.float32, shape=(None, num_actions))
      self.weights = tf.placeholder(tf.float32, shape=(None, num_actions))

      self._weight_decay = kwargs.get('weight_decay', 0.0)

      # Build up the hidden layers for the network
      # Start by reshaping the input to work with the 2D convolutional tensors
      current_layer = self.input

      for layer in hidden_layers:
         current_layer = layer.build(current_layer)

      self.output = current_layer

      # Set the objective to the L2-norm of the residual
      self.loss = l2_loss(self.output - self.target)
      self._weight_cost = tf.add_n([tf.nn.l2_loss(v) for v in tf.trainable_variables()])
      self._objective = self.loss


   def objective(self):
      """
      Return the objective tensor of this network
      """

      return self._objective


   def get_feed_dict(self, data):
      """
      Create a feed dictionary for this model
      """

      return {self.input: data['input'], self.target: data['target'], self.weights: data['weight']}


   def train(self, train_step, data):
      """
      Train on the input data (x) and the target (y).  The train step is some optimizer
      """

      train_step.run(feed_dict=self.get_feed_dict(data))