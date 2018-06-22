# Sorting sounds by emotion

import os
import shutil

cwd = os.getcwd()

soundDir = os.path.join(cwd, "wav")

for soundFilename in os.listdir(soundDir):
    if (len(soundFilename.split(".")) == 2):
        print soundFilename
        emotion = soundFilename[-6]

        src = os.path.join(soundDir, soundFilename)
        dest = os.path.join(cwd, emotion, soundFilename)

        shutil.move(src, dest)
