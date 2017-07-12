#!/usr/bin/python

import os
import argparse
import shutil
import numpy as np
import cv2
import tensorflow as tf
import tfimage as im



projects = [d for d in os.listdir('projects') if os.path.isdir(os.path.join('projects', d))]


parser = argparse.ArgumentParser()


parser.add_argument("project", choices=projects)
parser.add_argument("cmd", choices=['prepraw', 'prepvals'])
args = parser.parse_args()

train_path = os.path.join('projects', args.project, 'train')
model_path = os.path.join('projects', args.project, 'model')
test_path = os.path.join('projects', args.project, 'test')
val_path = os.path.join('projects', args.project, 'val')
rawA_path = os.path.join('projects', args.project, 'pix', 'rawA')
rawB_path = os.path.join('projects', args.project, 'pix', 'rawB')
rawC_path = os.path.join('projects', args.project, 'pix', 'rawC')
A_path = os.path.join('projects', args.project, 'pix', 'A')
B_path = os.path.join('projects', args.project, 'pix', 'B')
C_path = os.path.join('projects', args.project, 'pix', 'C')




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
    """Find most similar image.
    For every image in A_path find the the most similar image in B_path."""
    FLANN_INDEX_LSH = 6

    image_pairing = {}

    i = 0
    for imgA_name in sorted(os.listdir(A_path)):
        imgA_path = os.path.join(A_path, imgA_name)
        print "Searching for {0}".format(imgA_name)
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
        for imgB_name in sorted(os.listdir(B_path)):
            imgB_names.append(imgB_name)
            imgB_path = os.path.join(B_path, imgB_name)
            imgB = cv2.imread(imgB_path, 0)
            # print "Detecting and computing {0}".format(imgB_name)
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
        # print topimgidx
        # print imgB_names[topimgidx]
        image_pairing[imgA_name] = imgB_names[topimgidx]

        i += 1
        if limit > 0 and i > limit:
            break

    return image_pairing




def combine(pairing, A_path, B_path, dst_path):
    # clear output path
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    os.mkdir(dst_path)
    with tf.Session() as sess:
        for imgA_name, imgB_name in pairing.items():
            imgA = im.load(os.path.join(A_path, imgA_name))
            imgB = im.load(os.path.join(B_path, imgB_name))

            # make sure that dimensions are correct
            height, width, _ = imgA.shape
            if height != imgB.shape[0] or width != imgB.shape[1]:
                raise Exception("differing sizes")

            # convert both images to RGB if necessary
            if imgA.shape[2] == 1:
                imgA = im.grayscale_to_rgb(images=imgA)

            if imgB.shape[2] == 1:
                imgB = im.grayscale_to_rgb(images=imgB)

            # remove alpha channel
            if imgA.shape[2] == 4:
                imgA = imgA[:,:,:3]

            if imgB.shape[2] == 4:
                imgB = imgB[:,:,:3]

            imgC = np.concatenate([imgA, imgB], axis=1)
            im.save(imgC, os.path.join(dst_path,imgA_name))




if args.cmd == 'prepraw':
    pad(rawA_path, A_path)
    pad(rawB_path, B_path)
    pairs = flann(A_path, B_path, 0)
    # print pairs
    combine(pairs, A_path, B_path, train_path)
elif args.cmd == 'prepvals':
    pad(rawC_path, C_path)
    pairs = flann(A_path, C_path, 0)
    combine(pairs, A_path, C_path, val_path)
