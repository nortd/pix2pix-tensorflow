"""Train a convnet to enhance low resolution images.

1. Start with a set of training images.
2. Create a second set by downscaling it.
"""

import os
import argparse

import ops
import path
path.init("enhance")


# projects = [d for d in os.listdir('projects') if os.path.isdir(os.path.join('projects', d))]
parser = argparse.ArgumentParser()
# parser.add_argument("project", choices=projects)
parser.add_argument("cmd", choices=['prep', 'train', 'test', 'push', 'pull'])
parser.add_argument("--epochs", dest="epochs", type=int, default=200)
args = parser.parse_args()


if args.cmd == 'prep':
    ops.fixextension(path.rawA)
    ops.crop_square_resize(path.rawA, path.A, 256, 256)
    ops.crop_square_resize(path.A, path.B, 64, 64, 256, 256)
    ops.combine(path.A, path.B, path.train)
elif args.cmd == 'train':
    ops.train(path.model, path.train, args.epochs)
elif args.cmd == 'test':
    ops.test(path.model, path.val, path.test)
elif args.cmd == 'push':
    ops.push('enhance')
elif args.cmd == 'pull':
    ops.pull('enhance')
