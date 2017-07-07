#!/usr/bin/python

import os
import argparse
import shutil
import numpy as np



projects = [d for d in os.listdir('projects') if os.path.isdir(os.path.join('projects', d))]


parser = argparse.ArgumentParser()

parser.add_argument("project", choices=projects)
parser.add_argument("cmd", choices=['train', 'test', 'pad', 'resize', 'genb', 'combine', 'prepraw', 'push', 'pull'])
parser.add_argument("--epochs", dest="epochs", type=int, default=200)
args = parser.parse_args()

train_path = os.path.join('projects', args.project, 'train')
model_path = os.path.join('projects', args.project, 'model')
test_path = os.path.join('projects', args.project, 'test')
val_path = os.path.join('projects', args.project, 'val')
raw1_path = os.path.join('projects', args.project, 'pix', 'raw1')
raw2_path = os.path.join('projects', args.project, 'pix', 'raw2')
A1_path = os.path.join('projects', args.project, 'pix', 'A1')
A2_path = os.path.join('projects', args.project, 'pix', 'A2')
B1_path = os.path.join('projects', args.project, 'pix', 'B1')
B2_path = os.path.join('projects', args.project, 'pix', 'B2')



def grabcut(imgo):
    height, width = imgo.shape[:2]

    #Create a mask holder
    mask = np.zeros(imgo.shape[:2],np.uint8)

    #Grab Cut the object
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)

    # rect = (0,0,width,height)
    rect = (1,0,width,height)
    cv2.grabCut(imgo, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img1 = imgo*mask[:,:,np.newaxis]

    #Get the background
    background = imgo - img1

    #Change all pixels in the background that are not black to white
    background[np.where((background > [0,0,0]).all(axis = 2))] =[255,255,255]

    #set to black
    # img1.setTo(cv2.Scalar(0,0,0)) np.zeros((512,512,3), np.uint8)


    #Add the background and the image
    # final = background + img1
    final = background + np.zeros(imgo.shape, np.uint8)

    #To be done - Smoothening the edges
    return final


def train():
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
      --which_direction BtoA""" % (model_path, args.epochs, train_path)
    os.system(cmd)


def test():
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


def pad(source, target):
    # clear output path
    if os.path.exists(target):
        shutil.rmtree(target)
    os.mkdir(target)
    # regenerate
    from PIL import Image
    for img_path in os.listdir(source):
        img = Image.open(os.path.join(source, img_path))
        # return a white-background-color image having the img in exact center
        size = (max(img.size),)*2
        layer = Image.new('RGB', size, (255,255,255))
        layer.paste(img, tuple(map(lambda x:(x[0]-x[1])/2, zip(size, img.size))))
        # resize
        layer = layer.resize((256, 256), Image.ANTIALIAS)
        if not os.path.exists(target):
            os.makedir(target)
            # os.makedirs(target)
        layer.save(os.path.join(target, img_path))


# def resize():
#     # clear output path
#     shutil.rmtree(A1_path)
#     os.mkdir(A1_path)
#     # regenerate
#     cmd = """python tools/process.py \
#         --input_dir %s \
#         --operation resize \
#         --output_dir %s""" % (raw1_path, A1_path)
#     os.system(cmd)


def genb(source, target):
    # clear output path
    if os.path.exists(target):
        shutil.rmtree(target)
    os.mkdir(target)
    # regenerate
    import cv2
    for img_path in os.listdir(source):
        img = cv2.imread(os.path.join(source, img_path))
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        img = cv2.cvtColor(thresh,cv2.COLOR_GRAY2BGR)
        # img_cut = grabcut(img)
        cv2.imwrite(os.path.join(target, img_path), img)
        # ret, thresh = cv2.threshold(gray,220,255,cv2.THRESH_BINARY)
        # ret, thresh = cv2.threshold(gray,0,255,cv2.ADAPTIVE_THRESH_MEAN_C+cv2.THRESH_OTSU)
        # ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # thresh = cv2.bitwise_not(thresh)  # invert
        # cv2.imwrite(os.path.join(target, img_path), thresh)


def combine(sourceA, sourceB, target):
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
    for file_ in path:
        file_path = os.path.join(path, file_)
        base, ext_ = os.path.splitext(file_path)
        if ext_.isupper():
            os.rename(file_path, base+ext_.lower())
    # os.system("rename 's/\.%s$/.%s/' %s" % (ext, extlow, os.path.join(path, "*."+ext)))


def prepraw():
    # fix names
    fixextension(raw1_path)
    fixextension(raw2_path)
    # rest
    pad(raw1_path, A1_path)
    pad(raw2_path, A2_path)
    genb(A1_path, B1_path)
    genb(A2_path, B2_path)
    combine(A1_path, B1_path, train_path)
    combine(A2_path, B2_path, val_path)


def push():
    cmd = """rsync -rcP -e ssh --delete %s/train/ stefan@teslahawk:/home/stefan/git/pix2pix-tensorflow/projects/%s/train/""" % \
          (os.path.join('projects', args.project), args.project)
    os.system(cmd)


def pull():
    cmd = """rsync -rcP -e ssh --delete stefan@teslahawk:/home/stefan/git/pix2pix-tensorflow/projects/%s/model/ %s/model/""" % \
          (args.project, os.path.join('projects', args.project))
    os.system(cmd)



if args.cmd == 'train':
    train()
elif args.cmd == 'test':
    test()
elif args.cmd == 'pad':
    pad(raw1_path, A1_path)
elif args.cmd == 'resize':
    resize()
elif args.cmd == 'genb':
    genb(A1_path, B1_path)
elif args.cmd == 'combine':
    combine()
elif args.cmd == 'prepraw':
    prepraw()
elif args.cmd == 'push':
    push()
elif args.cmd == 'pull':
    pull()
