import harris_corners as hc
import os
import shutil
import itertools
import random


cwd = os.getcwd()
image_dir = os.path.join(cwd, "unsorted")
numImages = 15

for i in range(13):
	if not os.path.isDir(os.path.join(os.path.dirname(cwd), "images", str(i))):
		os.mkdir(os.path.join(os.path.dirname(cwd), "images", str(i)))

for filename in os.listdir(image_dir):
	if filename == ".DS_Store":
		image_path = os.path.join(image_dir, filename)
		os.remove(image_path)

	else:
		image_path = os.path.join(image_dir, filename)

		num_corners = hc.count_corners(image_path)

		#print "moving file! corners: " + str(num_corners)
		corner_dir = os.path.join(image_dir, str(num_corners))

		if (os.path.exists(corner_dir)):
			shutil.move(image_path, os.path.join(corner_dir,filename))
		else:
			os.remove(image_path)


for corners in range(13):
    cornerdir = os.path.join(os.path.dirname(cwd), "images", str(corners))

    linecount = 0
    pscount = 0

    for shape in os.listdir(cornerdir):
        if shape.find("LC") != -1:
            linecount += 1
            continue

        if shape.find("PS") != -1:
            pscount += 1
            continue



    lc_choices = random.sample(range(linecount),numImages)
    ps_choices = random.sample(range(pscount),numImages)

    #picking random lc images:
    for num in range(numImages):
        lc = lc_choices[num]
        lc_file = "LC_" + str(lc)
        shutil.move(os.path.join(cornerdir, lc_file), os.path.join(cornerdir, "LC" + str(num)))

    #picking random ps images
    for num2 in range(15):
        ps = ps_choices[num2]
        ps_file = "PS_" + str(ps)
        shutil.move(os.path.join(cornerdir, ps_file), os.path.join(cornerdir,"PS" + str(num2)))


    for file in os.listdir(cornerdir):
        if file.find("_") != -1:
            os.remove(os.path.join(cornerdir,file))


for zscore in range(13):
    zscore_dir = os.path.join(type_dir, str(zscore))

    LC_dir = (os.path.join(type_dir, str(zscore), "LC"))
    if not os.path.exists(LC_dir):
        os.mkdir(LC_dir)

    PS_dir = (os.path.join(type_dir, str(zscore), "PS"))
    if not os.path.exists(PS_dir):
        os.mkdir(PS_dir)

    for file in os.listdir(zscore_dir):
        if os.path.isdir(os.path.join(zscore_dir, file)):
            continue

        if file.find("LC") != -1:
            shutil.move(os.path.join(zscore_dir, file),
                        os.path.join(LC_dir, file))
        elif file.find("PS") != -1:
            shutil.move(os.path.join(zscore_dir, file),
                        os.path.join(PS_dir, file))
