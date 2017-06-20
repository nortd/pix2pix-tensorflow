
import os
import argparse
import numpy as np



projects = [d for d in os.listdir('projects') if os.path.isdir(os.path.join('projects', d))]


parser = argparse.ArgumentParser()

#
# subparsers = parser.add_subparsers(help="subparsers")
#
# # train subparser
# parser_train = subparsers.add_parser('train')
#
# #use that as you would any other argument parser
# parser_scream.add_argument('words', nargs='*')
#
# #set_defaults is nice to call a function which is specific to each subparser
# parser_scream.set_defaults(func=scream)
#
# #repeat for our next sub-command
# parser_count = subparsers.add_parser('count')
# parser_count.add_argument('count')
# parser_count.set_defaults(func=count)



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



parser.add_argument("--cmd", required=True, choices=['train', 'test', 'pad', 'resize', 'genb', 'combine', 'push', 'pull'])
parser.add_argument("--project", required=True, choices=projects)
args = parser.parse_args()
print args.project

train_path = os.path.join('projects', args.project, 'train')
model_path = os.path.join('projects', args.project, 'model')
test_path = os.path.join('projects', args.project, 'test')
val_path = os.path.join('projects', args.project, 'val')
raw_path = os.path.join('projects', args.project, 'pix', 'raw')
A_path = os.path.join('projects', args.project, 'pix', 'A')
B_path = os.path.join('projects', args.project, 'pix', 'B')
max_epochs = 200

if args.cmd == 'train':
    cmd = """python pix2pix.py \
      --mode train \
      --output_dir %s \
      --max_epochs %s \
      --input_dir %s \
      --which_direction BtoA""" % (model_path, max_epochs, train_path)
    os.system(cmd)
elif args.cmd == 'test':
    cmd = """python pix2pix.py \
      --mode test \
      --output_dir %s \
      --input_dir %s \
      --checkpoint %s""" % (test_path, val_path, model_path)
    os.system(cmd)
elif args.cmd == 'pad':
    from PIL import Image
    for img_path in os.listdir(raw_path):
        img = Image.open(os.path.join(raw_path, img_path))
        # return a white-background-color image having the img in exact center
        size = (max(img.size),)*2
        layer = Image.new('RGB', size, (255,255,255))
        layer.paste(img, tuple(map(lambda x:(x[0]-x[1])/2, zip(size, img.size))))
        # resize
        layer = layer.resize((256, 256), Image.ANTIALIAS)
        if not os.path.exists(A_path):
            os.makedir(A_path)
            # os.makedirs(A_path)
        layer.save(os.path.join(A_path, img_path))
elif args.cmd == 'resize':
    cmd = """python tools/process.py \
        --input_dir %s \
        --operation resize \
        --output_dir %s""" % (raw_path, A_path)
    os.system(cmd)
elif args.cmd == 'genb':
    import cv2
    for img_path in os.listdir(A_path):
        img = cv2.imread(os.path.join(A_path, img_path))
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        img = cv2.cvtColor(thresh,cv2.COLOR_GRAY2BGR)
        # img_cut = grabcut(img)
        cv2.imwrite(os.path.join(B_path, img_path), img)
        # ret, thresh = cv2.threshold(gray,220,255,cv2.THRESH_BINARY)
        # ret, thresh = cv2.threshold(gray,0,255,cv2.ADAPTIVE_THRESH_MEAN_C+cv2.THRESH_OTSU)
        # ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        # thresh = cv2.bitwise_not(thresh)  # invert
        # cv2.imwrite(os.path.join(B_path, img_path), thresh)
elif args.cmd == 'combine':
    cmd = """python tools/process.py \
        --input_dir %s \
        --b_dir %s \
        --operation combine \
        --output_dir %s""" % (A_path, B_path, train_path)
    os.system(cmd)
elif args.cmd == 'push':
    cmd = """rsync -rcP -e ssh --delete %s/ stefan@teslahawk:/home/stefan/git/pix2pix-tensorflow/projects/%s/""" % \
          (os.path.join('projects', args.project), args.project)
    os.system(cmd)
elif args.cmd == 'pull':
    cmd = """rsync -rcP -e ssh --delete stefan@teslahawk:/home/stefan/git/pix2pix-tensorflow/projects/%s/ %s/""" % \
          (args.project, os.path.join('projects', args.project))
    os.system(cmd)
