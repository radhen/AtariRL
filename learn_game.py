##
##
##

# Import libraries to simulate Atari and display results
from ale_python_interface import ALEInterface
import pygame
from pygame.locals import *

import numpy as np
import os

import scipy.ndimage as ndimage

from models.DeepQNetwork import *

from controllers import DQNController, EpsilonController
from NetworkParameters import NATURE, ARXIV
from memory import ReplayMemory
 
from environment import AtariEnvironment

import tensorflow as tf

from listeners.checkpoint_recorder import *
from listeners.tensorboard_monitor import *


#from replay_memory import *


class Counter:
	"""
	Simple class to maintain a shared counter between objects
	"""

	def __init__(self, initial_count=0):
		"""
		"""

		self.count = initial_count


	def step(self):
		"""
		Increment the counter
		"""

		self.count += 1



class AtariGameInterface:
	"""
	"""

	def __init__(self, game_filename, controller, replay_memory, counter, **kwargs):
		"""
		Load the game and create a display using pygame
		"""

		self.environment = AtariEnvironment(game_filename)
		
		# Hang on to the provided controller and replay memory
		self.controller = controller
		self.replay_memory = replay_memory

		self.evaluate = False

		# Maximum number of no-op that can be performed at the start of an episode
		self.noop_max = kwargs.get('noop_max', 30)
		self.action_repeat = kwargs.get('action_repeat', 4)

		self.counter = counter

		# Listeners for storing parameters, tensorboard, etc.
		self.listeners = []
		

	def add_listener(self, listener):
		"""
		"""

		self.listeners.append(listener)


	def learn(self):
		"""
		Allow for controller to learn while playing the game
		"""

		# Reset the game to start a new episode
		self.environment.reset_game()

		num_lives = self.environment.lives()	

		score = 0

		for listener in self.listeners:
			listener.start_episode({})


		# Wait a random number of frames before starting
		for i in range(np.random.randint(self.noop_max)):
			self.environment.act(0)

		while not self.environment.terminal():
			self.environment.update_screen()

			state = self.environment.get_reduced_screen()
			action, Q = self.controller.act(state)

			# Run the action 4 times
			reward = 0.0
			for i in range(self.action_repeat):
				reward += self.environment.act(action)

			score += reward

			self.counter.step()

			# Cap reward to be between -1 and 1
			reward = min(max(reward, -1.0), 1.0)

			for listener in self.listeners:
				listener.record({'Q': np.max(Q), 'reward': reward, 'action': action})

			is_terminal = self.environment.terminal() or self.environment.lives() != num_lives
			num_lives = self.environment.lives()

			self.replay_memory.record(state, action, reward, is_terminal)

		for listener in self.listeners:
			listener.end_episode({'score': score})

		return score


	def play(self, epsilon=0.1):
		"""
		Allow the controller to play the game
		"""

		total_score = 0

		old_show_while_training = self.show_while_training
		self.show_while_training = True

		# Reset the game to start a new episode
		self.environment.reset_game()

		while not self.environment.terminal():
			self.environment.update_screen()

			state = self.environment.get_reduced_screen()
			action_num = self.controller.base_controller.act(state)
			if np.random.random() < epsilon:
				action = np.random.randint(len(self.move_list))

			for i in range(self.action_repeat):
				reward = self.environment.act(action)
				total_score += reward
				self.environment.update_screen()


		self.show_while_training = old_show_while_training

		return total_score


sess = tf.InteractiveSession()
counter = Counter(2000000)

replay_memory = ReplayMemory(1000000)
dqn_controller = DQNController((84,84,4), NATURE, 4, replay_memory, counter, tf_session=sess)
controller = EpsilonController(dqn_controller, 4, counter)
agi = AtariGameInterface('Breakout.bin', controller, replay_memory, counter)

# Create a Tensorboard monitor and populate with the desired summaries
tensorboard_monitor = TensorboardMonitor('./log', sess, counter)
tensorboard_monitor.add_scalar_summary('score', 'per_game_summary')
tensorboard_monitor.add_scalar_summary('training_loss', 'training_summary')
for i in range(4):
	tensorboard_monitor.add_histogram_summary('Q%d_training' % i, 'training_summary')

agi.add_listener(CheckpointRecorder(dqn_controller.dqn, replay_memory, counter, './checkpoints'))
agi.add_listener(tensorboard_monitor)
dqn_controller.add_listener(tensorboard_monitor)

sess.run(tf.global_variables_initializer())

# Restore things
dqn_controller.dqn.restore('./checkpoints/dqn/2000000')
dqn_controller.update_target_network()
replay_memory.load('./checkpoints/replay_memory/2000000')


def run():
	cur_episode = 0
	num_frames = 0
	while counter.count < 50000000:
		score = agi.learn()

		tensorboard_monitor.record({'score': score})

		elapsed_frames = counter.count - num_frames
		num_frames = counter.count
		print "Episode %d:  Total Score = %d\t# Frames = %d\tTotal Frames = %d\tEpsilon: %f" % (cur_episode, score, elapsed_frames, num_frames, controller.epsilon)
		cur_episode += 1

	print
	print "Done Training.  Playing..."

	for i in range(25):
		print "  Game #" + str(i), "- Score:", agi.play()

if __name__ == '__main__':
	run()

