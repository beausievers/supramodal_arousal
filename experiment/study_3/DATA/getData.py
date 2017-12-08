# Turning participant data JSONs into one large CSV file

import os
import csv
import json

cwd = os.getcwd()
mappingFilename = os.path.join(os.path.dirname(cwd), "GUI", 'conditionMapping.json')
with open(mappingFilename) as mappingFile:
    conditionMapping = json.load(mappingFile)

soundsParamFile = os.path.join(cwd, 'soundParameters.json')
imageParamFile = os.path.join(cwd, 'imageParameters.json')

with open(soundsParamFile) as f:
    soundParams = json.load(f)

with open(imageParamFile) as f:
    imageParams = json.load(f)

with open('positive.csv', 'a') as positiveCSV:
    writer = csv.writer(positiveCSV, delimiter=',')
    writer.writerow(["subID", "stimFile", "stimType", "bin", "corners", "SC",
                     "response", "boundingBoxArea", "areaRatio",
                     "duration", "numOnsets", "onsetStrength"])

with open('negative.csv', 'a') as positiveCSV:
    writer = csv.writer(positiveCSV, delimiter=',')
    writer.writerow(["subID", "stimFile", "stimType", "bin", "corners", "SC",
                     "response", "boundingBoxArea", "areaRatio",
                     "duration", "numOnsets", "onsetStrength"])

with open('matching.csv', 'a') as positiveCSV:
    writer = csv.writer(positiveCSV, delimiter=',')
    writer.writerow(["subID", "imageFile", "soundFile", "imageBin", "corners",
                     "soundBin", "SC", "response", "boundingBoxArea", "areaRatio",
                     "duration", "numOnsets", "onsetStrength"])

# go through all the participants
for i in range(len(conditionMapping)):

    # Positive condition
    if conditionMapping[str(i)] == "positive":
        # open CSV
        with open('positive.csv', 'a') as positiveCSV:
            writer = csv.writer(positiveCSV, delimiter=',')

            # write data from all runs
            for run in range(20):
                responseFile = os.path.join(os.path.dirname(cwd), "GUI", "output",
                                    str(i), 'stim_response_data_run' + str(run) + '.json')
                with open(responseFile) as f:
                    if os.stat(responseFile).st_size == 0:
                        print "empty trial: " + responseFile
                        break

                    responses = json.load(f)

                for stim, choice in responses.iteritems():
                    if choice == "NONE":
                        choice = "INAUDIBLE"
                    corner, stimName = stim.split("/")
                    if (stimName.find("PS") != -1 or
                        stimName.find("LC") != -1):
                        stimType = "image"
                        bbArea = imageParams[corner][stimName][1]
                        ratio = imageParams[corner][stimName][2]
                        writer.writerow([i, stimName, stimType,
                                         int(corner),
                                         int(corner) + 1, "NA",
                                         choice,
                                         bbArea, ratio,
                                         "NA", "NA", "NA"])

                    else:
                        stimType = "sound"
                        sc = soundParams[corner][stimName][0]
                        dur = soundParams[corner][stimName][1]
                        numOnsets = soundParams[corner][stimName][2]
                        onsetStrength = soundParams[corner][stimName][3]
                        writer.writerow([i, stimName, stimType,
                                         int(corner),
                                         "NA", sc,
                                         choice,
                                         "NA", "NA",
                                         dur, numOnsets, onsetStrength])




    # Negative condition
    elif conditionMapping[str(i)] == "negative":

        with open('negative.csv', 'a') as negativeCSV:
            writer = csv.writer(negativeCSV, delimiter=',')

            # write data from all runs
            for run in range(20):
                responseFile = os.path.join(os.path.dirname(cwd), "GUI", "output",
                                    str(i), 'stim_response_data_run' + str(run) + '.json')
                with open(responseFile) as f:
                    if os.stat(responseFile).st_size == 0:
                        print "empty trial: " + responseFile
                        break

                    responses = json.load(f)

                for stim, choice in responses.iteritems():
                    if choice == "NONE":
                        choice = "INAUDIBLE"
                    corner, stimName = stim.split("/")
                    if (stimName.find("PS") != -1 or
                        stimName.find("LC") != -1):
                        stimType = "image"
                        bbArea = imageParams[corner][stimName][1]
                        ratio = imageParams[corner][stimName][2]
                        writer.writerow([i, stimName, stimType,
                                         int(corner),
                                         int(corner) + 1, "NA",
                                         choice,
                                         bbArea, ratio,
                                         "NA", "NA", "NA"])

                    else:
                        stimType = "sound"
                        sc = soundParams[corner][stimName][0]
                        dur = soundParams[corner][stimName][1]
                        numOnsets = soundParams[corner][stimName][2]
                        onsetStrength = soundParams[corner][stimName][3]
                        writer.writerow([i, stimName, stimType,
                                         int(corner),
                                         "NA", sc,
                                         choice,
                                         "NA", "NA",
                                         dur, numOnsets, onsetStrength])

    # Matching condition
    else:

        with open('matching.csv', 'a') as matchingCSV:
            writer = csv.writer(matchingCSV, delimiter=',')

            # write data from all runs
            for run in range(20):
                presentFile = os.path.join(os.path.dirname(cwd), "GUI", "output",
                                    str(i), 'Match_presentation_order_data_run' + str(run) + '.json')
                with open(presentFile) as f:
                    if os.stat(presentFile).st_size == 0:
                        print "empty trial: " + responseFile
                        break

                    order = json.load(f)

                responseFile = os.path.join(os.path.dirname(cwd), "GUI", "output",
                                    str(i), 'Match_stim_response_data_run' + str(run) + '.json')
                with open(responseFile) as f:
                    responses = json.load(f)


                for index, pair in order.iteritems():
                    if responses[index] == "NONE":
                        choice = "INAUDIBLE"
                    else:
                        choice = responses[index]

                    imageData = pair[0].split("/")
                    soundData = pair[1].split("/")

                    bbArea = imageParams[imageData[-3]][imageData[-1]][1]
                    ratio = imageParams[imageData[-3]][imageData[-1]][2]

                    sc = soundParams[soundData[-3]][soundData[-1]][0]
                    dur = soundParams[soundData[-3]][soundData[-1]][1]
                    numOnsets = soundParams[soundData[-3]][soundData[-1]][2]
                    onsetStrength = soundParams[soundData[-3]][soundData[-1]][3]

                    writer.writerow([i, imageData[-1], soundData[-1],
                                        int(imageData[-3]), int(imageData[-3]) + 1,
                                        int(soundData[-3]), sc,
                                        choice,
                                        bbArea, ratio,
                                        dur, numOnsets, onsetStrength])
