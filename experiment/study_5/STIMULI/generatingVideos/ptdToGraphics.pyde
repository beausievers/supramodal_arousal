import os
import csv

def updateAxes():
    translate(w * 0.5, h, -10)
    rotateX(radians(80))
    rotateY(radians(2))

def drawAxes(l):
    pushMatrix()
    noStroke()
    strokeWeight(3)
    stroke(255, 0, 0)
    line(0, 0, 0, l, 0, 0)
    stroke(0, 255, 0)
    line(0, 0, 0, 0, l, 0)
    stroke(0, 0, 255)
    line(0, 0, 0, 0, 0, l)
    noStroke()
    popMatrix()

h = 300
w = 600
scaleFactor = 3

size(500,300,P3D)
background(0)
updateAxes()
stroke(255)


cwd = os.path.join(os.path.dirname(os.path.dirname(os.path.expanduser('~'))), 'renderingBodyMotion', 'ptd')
dataDir = os.path.join(cwd, 'ptd_data')

for subID in os.listdir(dataDir):
    subDir = os.path.join(dataDir, subID)

    if os.path.isdir(subDir):
        for movement in os.listdir(subDir):
            subDataTxt = os.path.join(subDir, movement)


            if (len(subDataTxt.split(".")) > 2):
                continue

            # Debugging
            #print subDataTxt
            subData = []
            with open(subDataTxt, 'r') as csvfile:
                dataReader = csv.reader(csvfile, delimiter=' ')
                maxFrames = int(next(dataReader)[0])
                for row in dataReader:
                    subData.append([float(x) for x in row[:-1]])

            for frame in range(maxFrames):
                background(0)
                for i in range(15):
                    pushMatrix()
                    translate(subData[frame][i*3]*scaleFactor,
                            subData[frame][i*3+1]*scaleFactor,
                            subData[frame][i*3+2]*scaleFactor)
                    sphere(5)
                    popMatrix()

                save(subID + "/" + movement.split(".")[0] + "/" + str(frame+1).zfill(4) + ".png")
