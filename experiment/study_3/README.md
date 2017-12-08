# Universal Contours
Generating and presenting stimuli for universal contours study.

### STIMULI
Directory contains relevant subdirectories with the 390 shapes and 390 sounds that were used for the study. *STIMULI* directory also containing jupyter notebooks for looking at the variance in the relevant parameters of shapes and sounds, as well as code for generating new shapes or sounds.

Once stimuli are generated, `getParameters.py` is used to generate stimuli parameter JSONs for further analysis. Stimuli parameter JSONs are placed in *DATA* directory.

#### images and sounds

All stimuli used for the study are found in their respective directories. Directories are sorted according to zscored number of corners or spectral centroid. Within each numbered subdirectory, there are directories for each generating method and stimuli generated using that method contained within.

#### generating_images  

The two algorithms for generating shapes are contained within `line_curve.pyde` and `pseudoAmeoba.pyde`. To run either, open in *Processing* and click run. This will output all shapes generated into a subdirectory named *unsorted*.

To pick some random subset of images to be used and sort according to corner count, call `pickImages.py`


#### generating_sounds

The three methods used to create and save the sounds can all be found in the `Making and Saving sounds` notebook. As noted in the Jupyter notebook, cells from within the notebook must be run individually in order to generate the desired number of sounds. This will output all sounds into a subdirectory named *unsorted*.

To pick some random subset of sounds to be used and sort them according to spectral centroid, run the code within the `Picking and Sorting sounds` notebook.

### GUI

3 different conditions - negative arousal, positive arousal, and matching. All created using `psychopy` library. Conditions are assigned randomly; conditions for each subjectID can be found in `conditionMapping.json`.

To generate new subjectIDs assigned randomly to conditions and a new conditionMapping JSON, call `getSubjectIDs.py`.

**To run**: call `run.py`. Subject ID and subject demographics must be entered into the code in `run.py` manually before beginning task. `run.py` will then run the appropriate arousal or matching task, referenced from mapping JSON.

Output will be in the form of a directory for the subjectID containing JSON files of presentation order data and response data. Subject data directories are placed in *output* directory from within *GUI* directory. If not already exists, must manually create directory.

### DATA

Converts all relevant subject data (from *GUI/output/* directory) into CSV for each condition.

**To run**: call `getData.py`. Directory must contain stimuli parameter JSONs to build CSVs. Relevant parameter JSONs are created using `getParameters.py` from within the *STIMULI* directory.
