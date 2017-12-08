"""Harris corner detection for Universal Contours paper."""

import skimage.io
import skimage.color
import skimage.filters
import skimage.exposure
import skimage.feature
import skimage.morphology

import matplotlib.pyplot as plt
import seaborn as sns


def count_corners(img_path, disk_size=1, exposure_gamma=5, harris_sigma=5,
                  harris_min_distance=20, plot=False, title=None,
                  markersize=60, mew=8):
    """Detect and plot corners in img_path."""
    img = skimage.io.imread(img_path)
    img = skimage.color.rgb2gray(img)

    # Convert to 8 bit to speed processing
    img = skimage.img_as_ubyte(img)

    # Smooth the image to compensate for pencil drawings,
    # pressure irregularities, etc.
    img = skimage.filters.rank.median(img, skimage.morphology.disk(disk_size))

    img = skimage.exposure.adjust_gamma(img, gamma=exposure_gamma)


    coords = skimage.feature.corner_peaks(
        skimage.feature.corner_harris(img, sigma=harris_sigma),
        min_distance=harris_min_distance
    )
    num_corners = len(coords)

    if plot:
        sns.set_style("white")
        fig, ax = plt.subplots(figsize=(40, 40))
        ax.imshow(img, interpolation='nearest', cmap=plt.cm.gray)
        ax.plot(coords[:, 1], coords[:, 0], '+r', markersize=markersize, mew=mew)

        if title is not None:
            ax.set_title(title + ", {0} corners".format(num_corners))
        plt.show()

        if title is None:
            print(img_path)
            print("{0} corners.".format(num_corners))

    return(num_corners)
