"""Train a convnet to enhance low resolution images.

1. Start with a set of training images.
2. Create a second set by downscaling it.
"""

import os
import argparse
import shutil
import numpy as np
import cv2
import tensorflow as tf
import tfimage as im

import ops
import path
path.init("enhance")


# projects = [d for d in os.listdir('projects') if os.path.isdir(os.path.join('projects', d))]
parser = argparse.ArgumentParser()
# parser.add_argument("project", choices=projects)
parser.add_argument("cmd", choices=['prep', 'prepvals'])
args = parser.parse_args()


if args.cmd == 'prep':
    ops.fixextension(path.rawA)
    ops.crop_resize(path.rawA, path.A, 256, 256)
    ops.crop_resize(path.A, path.B, 64, 64)
    combine(path.A, path.B, path.train)
elif args.cmd == 'train':
    ops.train(path.model, path.train, 400)
elif args.cmd == 'test':
    ops.test(path.model, path.val, path.test)
# elif args.cmd == 'prepvals':
#     pad(rawC_path, C_path)
#     pairs = flann(A_path, C_path, 0)
#     combine(pairs, A_path, C_path, val_path)
