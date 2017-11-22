"""Train NN to enhance low resolution images.

1. 'extract' images from video.
2. 'prep' training set
3.
"""

import os
import argparse

import ops
import path
import vm

# PROJECT = "enhance2"
PROJECT = "enhance_terminatorsunsets"
TRAINGVIDEO = "../../../terminator.mp4"
TRAINGVIDEO_FPS = "1/4"


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
parser.add_argument("cmd", choices=['extract', 'videofy', 'prep', 'escalate', 'train', 'train_remote', 'test', 'push', 'pull', 'pull_from_relay'])
parser.add_argument("--epochs", dest="epochs", type=int, default=200)
parser.add_argument("--size", dest="size", type=int, default=256)
args = parser.parse_args()

if args.cmd == 'extract':
   ops.video_extract(TRAINGVIDEO, path.rawA, TRAINGVIDEO_FPS)
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
elif args.cmd == 'escalate':
    escalate()
elif args.cmd == 'train':
    ops.train(path.model, path.train, args.epochs, args.size)
elif args.cmd == 'init_remote':
    # create dirs and git clone repo
    os.system('ssh %s "mkdir git; cd git; git clone %s; mkdir %s/projects"'
              % (vm.GPU_INSTANCE, path.GIT_REPO_URL, path.GIT_REPO_NAME))
    # install packages
    os.system('ssh %s "sudo apt-get install -y ffmpeg python-imaging python3-pil"'
              % (vm.GPU_INSTANCE))
elif args.cmd == 'train_remote':
    """Run on GPU_INSTANCE via ssh and tmux.
    To keep a process running I use:
        tmux -d python script.py
    Manually running tmux first works too. Detaching is done with [ctrl]-[b], [d].
    And a running tmux session can be reatached with: tmux attach
    """
    os.system('ssh %s "cd git; git pull"'
              % (vm.GPU_INSTANCE))
    os.system('ssh %s "python git/pix2pix-tensorflow/project_enhance.py extract"'
              % (vm.GPU_INSTANCE))
    os.system('ssh %s "python git/pix2pix-tensorflow/project_enhance.py prep"'
              % (vm.GPU_INSTANCE))
    vm.call_remote_cmd_in_tmux(vm.GPU_INSTANCE, "python git/pix2pix-tensorflow/project_enhance.py train")
elif args.cmd == 'test':
    ops.test(path.model, path.val, path.test, args.size)
elif args.cmd == 'push':
    ops.push(PROJECT)
elif args.cmd == 'pull':
    ops.pull(PROJECT)
elif args.cmd == 'pull_from_relay':
    ops.pull_from_relay(PROJECT)
