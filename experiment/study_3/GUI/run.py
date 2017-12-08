import json
import os

import arousal
import matching

cwd = os.getcwd()
mappingFilename = os.path.join(cwd, 'conditionMapping.json')
with open(mappingFilename) as mappingFile:
    conditionMapping = json.load(mappingFile)

##################################################
############# ENTER SUBJECT INFO HERE ############
##################################################

subjectID = 1
subjectAge = 10000
subjectGender = "deletethisone"
date = "TEST"

##################################################
##################################################
##################################################

if conditionMapping[str(subjectID)] == "positive":
    arousal.run(subjectID, "positive", subjectAge, subjectGender, date)

elif conditionMapping[str(subjectID)] == "negative":
    arousal.run(subjectID, "negative", subjectAge, subjectGender, date)

else:
    matching.run(subjectID, subjectAge, subjectGender, date)
