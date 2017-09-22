from models.parts import *

# Network used in NIPS workshop paper
NIPS  = [Convolutional((8,8), 16, name='conv1', stride=4),
          Convolutional((4,4), 32, name='conv2', stride=2),
          Flatten(name='flatten'),
          FullConnection(256, name='full1')
        ]

# Network used in Nature paper
NATURE = [Convolutional((8,8), 32, name='conv1', stride=4),
           Convolutional((4,4), 64, name='conv2', stride=2),
           Convolutional((3,3), 64, name='conv3', stride=1),
           Flatten(name='flatten'),
           FullConnection(512, name='full1')
         ]

# Network used for deuling DQN.  3-tuple, 2nd & 3rd elements are value and
# advantage streams
DUELING = ([Convolutional((8,8), 32, name='conv1', stride=4),
            Convolutional((4,4), 64, name='conv2', stride=2),
            Convolutional((3,3), 64, name='conv3', stride=1),
            Flatten(name='flatten')],
           [FullConnection(512, name='full_value')],
           [FullConnection(512, name='full_advantage')]
          )



