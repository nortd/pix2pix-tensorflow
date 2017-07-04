#!/usr/bin/python

import os
import argparse
import shutil
import numpy as np
import cv2



projects = [d for d in os.listdir('projects') if os.path.isdir(os.path.join('projects', d))]


parser = argparse.ArgumentParser()


parser.add_argument("project", choices=projects)
parser.add_argument("cmd", choices=['prepraw'])
args = parser.parse_args()

train_path = os.path.join('projects', args.project, 'train')
model_path = os.path.join('projects', args.project, 'model')
test_path = os.path.join('projects', args.project, 'test')
val_path = os.path.join('projects', args.project, 'val')
rawA_path = os.path.join('projects', args.project, 'pix', 'rawA')
rawB_path = os.path.join('projects', args.project, 'pix', 'rawB')
A_path = os.path.join('projects', args.project, 'pix', 'A')
B_path = os.path.join('projects', args.project, 'pix', 'B')




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


def flann(A_path, B_path, limit=0):
    FLANN_INDEX_LSH = 6

    i = 0
    for img_ in sorted(os.listdir(A_path)):
        imgA_path = os.path.join(A_path, img_)
        print "Searching for {0}".format(img_)
        imgA = cv2.imread(imgA_path, 0)
        brisk = cv2.BRISK()
        kpA, desA = brisk.detectAndCompute(imgA, None)
        index_params= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2
        search_params = dict(checks=50)   # or pass empty dictionary
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        imgB_names = []
        for img__ in sorted(os.listdir(B_path)):
            imgB_names.append(img__)
            imgB_path = os.path.join(B_path, img__)
            imgB = cv2.imread(imgB_path, 0)
            # print "Detecting and computing {0}".format(img__)
            kpB, desB = brisk.detectAndCompute(imgB, None)
            # print "Adding..."
            flann.add([desB])


        print len(flann.getTrainDescriptors()) #verify that it actually took the descriptors in

        # print "Training..."
        flann.train()

        # print "Matching..."
        matchidxs = []
        matches = flann.knnMatch(desA, k=2)
        for match in matches:
            for matchpart in match:
                matchidxs.append(matchpart.imgIdx)
        topimgidx = max(matchidxs, key=matchidxs.count)
        print topimgidx
        print imgB_names[topimgidx]

        i += 1
        if limit > 0 and i > limit:
            break


if args.cmd == 'prepraw':
    pad(rawA_path, A_path)
    pad(rawB_path, B_path)
    flann(A_path, B_path, 4)
