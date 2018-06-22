# Universal Contours: Study 5

Generating and presenting stimuli for universal contours study 5.

### STIMULI
This directory must be populated with stimuli from the PACO Body Movement Database and the Berlin Database of Emotional Speech. Directory contains script to generate videos (mp4) from text file with body movement parameters     (http://paco.psy.gla.ac.uk/index.php/res/download-data/viewcategory/9-ptd).

#### generatingVideos
Text files for body movement are given at link above as .ptd files. `renamePtdToTxt.py` takes .ptd files and turns into .txt files. `ptdToGraphics.pyde` uses processing to turn .txt files of joint locations into full body animations.

`sortSounds.py` and `sortVids.py` sort respective stimuli into subdirectories according to emotion tag given by database.

### GUI
_Note: Study 5 uses same GUI interface as Study 3. Therefore, allows for the use of multiple, randomized conditions. Turned off using "version" flag_

Created using psychopy library. Conditions are assigned randomly; conditions for each subjectID can be found in `conditionMapping.json`.

To generate new subjectIDs assigned randomly to conditions and a new conditionMapping JSON, call `getSubjectIDs.py`.

**To run**: call `run.py`. Subject ID and subject demographics must be entered into the code in `run.py` manually before beginning task.

Output will be in the form of a directory for the subjectID containing JSON files of presentation order data and response data. Subject data directories are placed in *output* directory from within *GUI* directory. If *output* directory does not already exist, user must manually create directory.

### DATA
`aggregateData.py` converts all relevant subject data (from *GUI/output/* directory) into one combined CSV.