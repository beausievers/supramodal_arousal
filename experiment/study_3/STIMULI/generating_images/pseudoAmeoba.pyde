# Distorted circle method.

import math
import itertools
import os

cwd = os.getcwd()

if not os.path.isdir(os.path.join(cwd, "unsorted")):
    os.mkdir(os.path.join(cwd, "unsorted"))

def pickRandomCombo(totalPoints, numCurvePoints):
    combo = list(itertools.combinations(range(totalPoints), numCurvePoints))
    pick = int(random(int(math.factorial(totalPoints)/math.factorial(numCurvePoints)/
                          math.factorial(totalPoints - numCurvePoints))))
    return combo[pick]

def getQuadrant(currentPoint):
    if (currentPoint[0] > 250) and (currentPoint[1] < 250):
        return 1
    elif (currentPoint[0] < 250) and (currentPoint[1] < 250):
        return 2
    elif (currentPoint[0] < 250) and (currentPoint[1] > 250):
        return 3
    else:
        return 4

def drawAmeoba(radius, centerX, centerY, numPoints, numCurvePoints):
    curvePointsInserted = 0
    positions = pickRandomCombo(numPoints + numCurvePoints, numCurvePoints)

    #points = []
    rad_increment = math.radians(360/(numPoints + numCurvePoints))

    currentRadians = 0
    vertex(centerX + radius, centerY)
    curveVertex(centerX + radius, centerY)

    currentPoint = (0,0)

    for i in range(numPoints + numCurvePoints):
        x = centerX + radius * math.cos(currentRadians)
        y = centerY + radius * math.sin(currentRadians)

        currentPoint = (x,y)

        #curveChoice = int(random(0,2))

        if (i == positions[curvePointsInserted]):
            #print "drawing curve!"
            #print currentPoint
            q = getQuadrant(currentPoint)
            #print "drawing in quadrant " + str(q)
            if (q == 1):
                curveVertex(random(250,450), random(50,250))
            elif (q == 2):
                curveVertex(random(50,250), random(50,250))
            elif (q == 3):
                curveVertex(random(50,250), random(250,450))
            elif (q == 4):
                curveVertex(random(250,450), random(250,450))

            if (curvePointsInserted < numCurvePoints-1):
                curvePointsInserted = curvePointsInserted + 1

        else:

            curveVertex(currentPoint[0],currentPoint[1])
            #points.append((x, y))

        currentRadians = currentRadians + rad_increment


    curveVertex (centerX + radius, centerY)
    curveVertex(centerX + radius, centerY)
    #return points


size(500, 500, P2D)

numImages = 0
for numPoints in range(3,15):
  for numCurves in range(10):
      for count in range(10):
          strokeWeight(2)
          background(255)
          curveTightness(0)
          s = createShape()
          beginShape()

          drawAmeoba(100,250,250,numPoints,numCurves)
          endShape()

          filename = os.path.join(cwd, "unsorted", "PS_" + str(numImages))

          save(filename)
          numImages += 1
