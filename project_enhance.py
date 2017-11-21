"""Train a convnet to enhance low resolution images.

1. Start with a set of training images.
2. Create a second set by downscaling it.
"""

import os
import argparse

import ops
import path

# PROJECT = "enhance2"
PROJECT = "enhance_terminatorsunsets"
TRAINGVIDEO = "../../../terminator.mp4"
TRAINGVIDEO_INTIME = ""
# TRAINGVIDEO_INTIME = "00:04:00"
TRAINGVIDEO_OUTTIME = ""
# TRAINGVIDEO_OUTTIME = "01:40:00"
# TRAINGVIDEO_OUTTIME = "00:04:20"
# TRAINGVIDEO_FRAMES = "1/10"  # 1 means about 1 image per minute
TRAINGVIDEO_FRAMES = "1"
TRAINGVIDEO_SIZE = "-2:256"
# TRAINGVIDEO_CROP = "256:256"
TRAINGVIDEO_CROP = ""

path.init(PROJECT)


# def escalate(sizes=[256,512,1024]):
def escalate(init_size=32, sizes=[256, 512, 1024, 2048]):
    """Run the model multiple times with increasing resolution."""
    first = True
    for s in sizes:
        if first:
            ops.clean_filenames(path.rawC, rename='pic_%s')
            ops.crop_square_resize(path.rawC, path.C, init_size, init_size, s, s)
            first = False
        else:
            # copy output to input
            ops.output_as_input(path.test, path.tempC)
            ops.clean_filenames(path.tempC, rename='pic_%s')
            ops.blur_resize(path.tempC, path.C, s, s, blur=0)

        ops.combine(path.C, path.C, path.val, s)
        # run model on input
        ops.test(path.model, path.val, path.test, s)



# projects = [d for d in os.listdir('projects') if os.path.isdir(os.path.join('projects', d))]
parser = argparse.ArgumentParser()
# parser.add_argument("project", choices=projects)
parser.add_argument("cmd", choices=['extract', 'videofy', 'prep', 'prepvals', 'prepvals2', 'escalate', 'train', 'train_remote', 'test', 'push', 'pull'])
parser.add_argument("--epochs", dest="epochs", type=int, default=200)
parser.add_argument("--size", dest="size", type=int, default=256)
args = parser.parse_args()

if args.cmd == 'extract':
    cwd = os.getcwd()
    os.chdir(path.rawA)
    intime = outtime = scale = crop = ""
    imageevery = "-r %s" % (TRAINGVIDEO_FRAMES)
    filepattern = "image%05d.jpg"
    if TRAINGVIDEO_SIZE != "":
        scale = "-vf scale=%s" % (TRAINGVIDEO_SIZE)
    if TRAINGVIDEO_CROP != "":
        crop = "-filter:v \"crop=%s\"" % (TRAINGVIDEO_CROP)
    if TRAINGVIDEO_INTIME != "":
        intime = "-ss %s" % (TRAINGVIDEO_INTIME)
    if TRAINGVIDEO_OUTTIME != "":
        outtime = "-ss %s" % (TRAINGVIDEO_OUTTIME)
    cmd = "ffmpeg %s -i %s %s %s %s -f image2  -q:v 2 %s %s" % (intime, TRAINGVIDEO, scale, crop, imageevery, outtime, filepattern)
    # cmd = """ffmpeg -i ../video.mp4  -r 1/2  -f image2  -q:v 2 image%05d.jpg"""
    os.system(cmd)
    os.chdir(cwd)
elif args.cmd == 'videofy':
    cwd = os.getcwd()
    os.chdir(os.path.join(path.test, 'images'))
    # cmd = "ffmpeg -r 30 -f image2 -s 256x256 -i pic_%d-outputs.png -vcodec libx264 -crf 25  -pix_fmt yuv420p ../out.mp4"
    cmd = 'ffmpeg -r 30 -i pic_%d-outputs.png -c:v libx264 -crf 15 -vf "fps=30,format=yuv420p" ../../out.mp4'
    os.system(cmd)
    os.chdir(cwd)
elif args.cmd == 'prep':
    ops.clean_filenames(path.rawA, rename='pic_%s')
    ops.crop_square_resize(path.rawA, path.A, args.size, args.size)
    ops.crop_square_resize(path.A, path.B, args.size/8, args.size/8, args.size, args.size)
    ops.combine(path.A, path.B, path.train, args.size)
elif args.cmd == 'prepvals':
    ops.clean_filenames(path.rawC, rename='pic_%s')
    # ops.crop_square_resize(path.rawC, path.C, args.size/8, args.size/8, args.size, args.size)
    ops.crop_square_resize(path.rawC, path.C, args.size/16, args.size/16, args.size, args.size)
    ops.combine(path.C, path.C, path.val, args.size)
elif args.cmd == 'prepvals2':
    ops.clean_filenames(path.rawC, rename='pic_%s')
    ops.crop_square_resize(path.rawC, path.C, args.size, args.size)
    ops.combine(path.C, path.C, path.val, args.size)
elif args.cmd == 'escalate':
    escalate()
    # """Use output images as input."""
    # output = os.path.join(path.test, 'images')
    # ops.copy_files(output, path.tempC, "*outputs.*")
    # ops.crop_square_resize(path.tempC, path.C, args.size/2, args.size/2, args.size, args.size)
    # ops.combine(path.C, path.C, path.val, args.size)
elif args.cmd == 'train':
    ops.train(path.model, path.train, args.epochs, args.size)
elif args.cmd == 'train_remote':
    """Run on GPU_INSTANCE via ssh and tmux.
    To keep a process running I use:
        tmux -d python script.py
    Manually running tmux first works too. Detaching is done with [ctrl]-[b], [d].
    And a running tmux session can be reatached with: tmux attach
    """
    cmd = 'ssh %s "tmux -d python git/pix2pix-tensorflow/project_enhance.py train"' % \
          (vm.GPU_INSTANCE)
    os.system(cmd)
elif args.cmd == 'test':
    ops.test(path.model, path.val, path.test, args.size)
elif args.cmd == 'push':
    ops.push(PROJECT)
elif args.cmd == 'pull':
    ops.pull(PROJECT)


# To init gpu instance:
#   mkdir git
#   git clone
#   mkdir projects
#   sudo apt-get install ffmpeg, python-imaging, python3-pil
#
