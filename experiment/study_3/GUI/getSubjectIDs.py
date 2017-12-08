# Adding/creating new subject IDS. specify number desired using numSubjects.

import random
import os
import json

numSubjects = 60
IDS = random.sample(range(numSubjects),numSubjects)
idConditions = {}

for num in range(20):
    idConditions[IDS[num]] = "positive"

for num in range(20,40):
    idConditions[IDS[num]] = "negative"

for num in range(40,60):
    idConditions[IDS[num]] = "matching"

cwd = os.getcwd()
conditionMappingFile = os.path.join(cwd, 'conditionMapping.json')

with open(conditionMappingFile, 'w') as f:
    json.dump(idConditions, f, sort_keys=True, indent=4)
