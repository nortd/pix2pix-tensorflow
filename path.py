"""Manage the directories of a roject.

Directories are as follows:
    projects/                 ... home of all the project data
    projects/<name>           ... a project
    ---
    project/<name>/train      ... training images
    projects/<name>/model     ... the trained model
    project/<name>/val        ... input pair images
    project/<name>/test       ... output images
    ---
    projects/<name>/pix       ... image staging
    projects/<name>/pix/A     ... target
    projects/<name>/pix/rawA  ... target, raw
    projects/<name>/pix/B     ... source
    projects/<name>/pix/rawB  ... source, raw
    projects/<name>/pix/C     ... input
    projects/<name>/pix/rawC  ... imput raw
"""

import os
import shutil

project = pix = train = model = test = val = ""
rawA = rawB = rawC = A = B = C = tempA = tempB = tempC = ""

def init(project_name):
    global project, pix, train, model, test, val
    global rawA, rawB, rawC, A, B, C, tempA, tempB, tempC
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
    tempA = os.path.join(project, 'pix', 'tempA')
    tempB = os.path.join(project, 'pix', 'tempB')
    tempC = os.path.join(project, 'pix', 'tempC')

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
    if not os.path.exists(tempA):
        os.mkdir(tempA)
    if not os.path.exists(tempB):
        os.mkdir(tempB)
    if not os.path.exists(tempC):
        os.mkdir(tempC)
