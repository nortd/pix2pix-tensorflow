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
parser.add_argument("cmd", choices=['extract', 'prep', 'prepvals', 'prepvals2', 'train', 'test', 'push', 'pull'])
parser.add_argument("--epochs", dest="epochs", type=int, default=200)
parser.add_argument("--size", dest="size", type=int, default=256)
parser.add_argument("--intime", default="")
parser.add_argument("--outtime", default="")
parser.add_argument("--extractsize", default="")
parser.add_argument("--imageevery", default="1/2")
args = parser.parse_args()

if args.cmd == 'extract':
    cwd = os.getcwd()
    os.chdir(path.rawA)
    intime = outtime = extractsize = ""
    imageevery = "-r %s" % (args.imageevery)
    filepattern = "image%05d.jpg"
    if args.extractsize != "":
        extractsize = "-s %s" % (args.extractsize)  # eg. hd720
    if args.intime != "":
        intime = "-ss %s" % (args.intime)
    if args.outtime != "":
        outtime = "-ss %s" % (args.intime)
    cmd = "ffmpeg %s -i ../video.mp4 %s %s -f image2  -q:v 2 %s %s" % (intime, extractsize, imageevery, outtime, filepattern)
    # cmd = """ffmpeg -i ../video.mp4  -r 1/2  -f image2  -q:v 2 image%05d.jpg"""
    os.system(cmd)
    os.chdir(cwd)
elif args.cmd == 'prep':
    ops.clean_filenames(path.rawA, rename='pic_%s')
    ops.crop_square_resize(path.rawA, path.A, args.size, args.size)
    ops.crop_square_resize(path.A, path.B, args.size/8, args.size/8, args.size, args.size)
    ops.combine(path.A, path.B, path.train, args.size)
elif args.cmd == 'prepvals':
    ops.clean_filenames(path.rawC, rename='pic_%s')
    ops.crop_square_resize(path.rawC, path.C, args.size/8, args.size/8, args.size, args.size)
    ops.combine(path.C, path.C, path.val, args.size)
elif args.cmd == 'prepvals2':
    ops.clean_filenames(path.rawC, rename='pic_%s')
    ops.crop_square_resize(path.rawC, path.C, args.size, args.size)
    ops.combine(path.C, path.C, path.val, args.size)
elif args.cmd == 'train':
    ops.train(path.model, path.train, args.epochs, args.size)
elif args.cmd == 'test':
    ops.test(path.model, path.val, path.test, args.size)
elif args.cmd == 'push':
    ops.push('enhance')
elif args.cmd == 'pull':
    ops.pull('enhance')
