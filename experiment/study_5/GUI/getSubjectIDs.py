# Adding/creating new subject IDS. specify number desired using numSubjects.

import random
import os
import json

numSubjects = 60
IDS = random.sample(range(numSubjects),numSubjects)
idConditions = {}
version = 2

if version == 1:
    for num in range(20):
        idConditions[IDS[num]] = "positive"

    for num in range(20,40):
        idConditions[IDS[num]] = "negative"

    for num in range(40,60):
        idConditions[IDS[num]] = "matching"

if version == 2:
    for num in range(60):
        idConditions[num] = "video"

cwd = os.getcwd()
conditionMappingFile = os.path.join(cwd, 'conditionMapping' + str(version) + '.json')

with open(conditionMappingFile, 'w') as f:
    json.dump(idConditions, f, sort_keys=True, indent=4)
