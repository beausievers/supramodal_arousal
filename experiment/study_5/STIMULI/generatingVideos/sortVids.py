#Sorting videos by emotion

import os
import shutil

cwd = os.getcwd()

videoDir = os.path.join(cwd, "videos")

for vidTitle in os.listdir(videoDir):
    print vidTitle
    if (len(vidTitle.split(".")) == 2):
        emotion = vidTitle.split("_")[2]

        src = os.path.join(videoDir, vidTitle)
        dest = os.path.join(cwd, emotion, vidTitle)

        shutil.move(src, dest)
