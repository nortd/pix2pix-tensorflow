"""Shared functions"""

import os
import shutil
from PIL import Image


def crop_resize(source, target, w, h):
    # clear output path
    if os.path.exists(target):
        shutil.rmtree(target)
    os.mkdir(target)
    for img_path in os.listdir(source):
        img = Image.open(os.path.join(source, img_path))
        image.thumbnail((w,h), Image.NEAREST)
        if not os.path.exists(target):
            os.makedir(target)
        image.save(os.path.join(target, img_path))


def train(model_path, train_path, epochs):
    """Train the convnet."""
    # clear output path
    if os.path.exists(model_path):
        shutil.rmtree(model_path)
    os.mkdir(model_path)
    # regenerate
    cmd = """python pix2pix.py \
      --mode train \
      --output_dir %s \
      --max_epochs %s \
      --input_dir %s \
      --which_direction BtoA""" % (model_path, epochs, train_path)
    os.system(cmd)


def test(model_path, val_path, test_path):
    """Run the model."""
    # clear output path
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    os.mkdir(test_path)
    # regenerate
    cmd = """python pix2pix.py \
      --mode test \
      --output_dir %s \
      --input_dir %s \
      --checkpoint %s""" % (test_path, val_path, model_path)
    os.system(cmd)


def combine(sourceA, sourceB, target):
    """Combine images from two dirs. Match by name."""
    # clear output path
    if os.path.exists(target):
        shutil.rmtree(target)
    os.mkdir(target)
    # regenerate
    cmd = """python tools/process.py \
        --input_dir %s \
        --b_dir %s \
        --operation combine \
        --output_dir %s""" % (sourceA, sourceB, target)
    os.system(cmd)


def fixextension(path):
    """Lowers the extension."""
    for file_ in path:
        file_path = os.path.join(path, file_)
        base, ext_ = os.path.splitext(file_path)
        if ext_.isupper():
            os.rename(file_path, base+ext_.lower())


def push(project_name):
    cmd = """rsync -rcP -e ssh --delete %s/train/ stefan@teslahawk:/home/stefan/git/pix2pix-tensorflow/projects/%s/train/""" % \
          (os.path.join('projects', project_name), project_name)
    os.system(cmd)


def pull(project_name):
    cmd = """rsync -rcP -e ssh --delete stefan@teslahawk:/home/stefan/git/pix2pix-tensorflow/projects/%s/model/ %s/model/""" % \
          (project_name, os.path.join('projects', project_name))
    os.system(cmd)
