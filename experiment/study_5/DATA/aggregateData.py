# Turning participant data JSONs into one large CSV file

import os
import csv
import json

cwd = os.getcwd()
mappingFilename = os.path.join(os.path.dirname(cwd), "GUI", 'conditionMapping.json')
with open(mappingFilename) as mappingFile:
    conditionMapping = json.load(mappingFile)

with open('data.csv', 'a') as positiveCSV:
    writer = csv.writer(positiveCSV, delimiter=',')
    writer.writerow(["subID", "stimFile", "stimType", "valenceRating", "arousalRating"])

# go through all the participants
for subID in range(len(conditionMapping)):

    with open('data.csv', 'a') as positiveCSV:
        writer = csv.writer(positiveCSV, delimiter=',')

        # write data from all runs
        for run in range(20):
            responseFile = os.path.join(os.path.dirname(cwd), "GUI", "output",
                                str(subID), 'videoRatings_run' + str(run) + '.json')

            orderFile = os.path.join(os.path.dirname(cwd), "GUI", "output",
                                str(subID), 'videoPresentationOrder_run' + str(run) + '.json')

            with open(responseFile) as f:
                responses = json.load(f)

            with open(orderFile) as f:
                order = json.load(f)

            # iterate through all trials per run
            for trial in range(11):

                if (order[trial].split(".")[1] == "mp4"): stimType = "videos"
                else: stimType = "sounds"

                writer.wrierow([subID, order[trial], stimType, responses[0], responses[1]])
