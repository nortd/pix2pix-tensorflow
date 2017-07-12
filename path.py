
import os
import shutil

project = pix = train = model = test = val = rawA = rawB = rawC = A = B = C = ""

def init(project_name):
    global project, pix, train, model, test, val, rawA, rawB, rawC, A, B, C
    project = os.path.join('projects', project_name)
    pix = os.path.join(project, 'pix')
    train = os.path.join(project, 'train')
    model = os.path.join(project, 'model')
    test = os.path.join(project, 'test')
    val = os.path.join(project, 'val')
    rawA = os.path.join(project, 'pix', 'rawA')
    rawB = os.path.join(project, 'pix', 'rawB')
    rawC = os.path.join(project, 'pix', 'rawC')
    A = os.path.join(project, 'pix', 'A')
    B = os.path.join(project, 'pix', 'B')
    C = os.path.join(project, 'pix', 'C')

    # create
    if not os.path.exists(project):
        os.mkdir(project)
    if not os.path.exists(pix):
        os.mkdir(pix)
    if not os.path.exists(train):
        os.mkdir(train)
    if not os.path.exists(model):
        os.mkdir(model)
    if not os.path.exists(test):
        os.mkdir(test)
    if not os.path.exists(val):
        os.mkdir(val)
    if not os.path.exists(rawA):
        os.mkdir(rawA)
    if not os.path.exists(rawB):
        os.mkdir(rawB)
    if not os.path.exists(rawC):
        os.mkdir(rawC)
    if not os.path.exists(A):
        os.mkdir(A)
    if not os.path.exists(B):
        os.mkdir(B)
    if not os.path.exists(C):
        os.mkdir(C)
