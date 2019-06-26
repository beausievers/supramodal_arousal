# A multi-sensory code for emotional arousal: data & materials

## Authors

Beau Sievers<sup>1</sup>, Caitlyn Lee<sup>1</sup>, William Haslett,<sup>2</sup> & Thalia Wheatley<sup>1</sup>

<sup>1</sup> Department of Psychological and Brain Sciences, Dartmouth College, Hanover, NH 03755

<sup>2</sup> Department of Biomedical Data Science, Geisel School of Medicine at Dartmouth, Hanover, NH 03755

Correspondence to: Thalia Wheatley, 6207 Moore Hall, Dartmouth College, Hanover, NH 03755. thalia.p.wheatley@dartmouth.edu

## About

This repository contains code, data, and materials for running the experiments and analyses described in the paper "A supramodal code for emotional arousal," available at: https://osf.io/t82wb/

None of this code was written with the express intention of facilitating reproducible experimentation or analysis, and it is not being actively maintained.

This repository does **NOT** contain the [Berlin Database of Emotional Speech](http://emodb.bilderbar.info/start.html) or the [PACO Body Movement Library](http://paco.psy.gla.ac.uk/index.php/res/download-data/viewcategory/5-body-movement-library), both of which are required to run the analyses for Study 4 and the experiment for Study 5.

## Software requirements.

All scripts were tested on Mac OS 10.14.5. Library requirements are listed in the following files:

 - `environment.yml`: a Python environment description for use with the conda package manager
 - `requirements.txt`: additional requirements for R and MatLab

## Why don't the notebook and paper results match exactly?

Because of the use of MCMC sampling and changes in required libraries that occured between manuscript drafting and final proofing, the analysis notebooks in this repository will produce very slightly different results than those reported in the paper. Regrettably, we did not record the RNG seed or the version numbers of the libraries originally used. (Yarik, you were right!)

## File structure

- `/experiment`: materials necessary to run the studies with new participants
- `/data`: data collected from our participants
- `/analysis`: code for running analyses and generating figures

## Citation

Sievers, B., Lee, C., Haslett, W., & Wheatley, T. (2017, December 8). A multi-sensory code for emotional arousal. Retrieved from osf.io/t82wb

## License

This software is made available under a BSD-style license. See the `LICENSE` file.

## Last updated

This document was last updated on June 25, 2019.
