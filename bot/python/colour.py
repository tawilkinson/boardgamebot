import discord
import numpy as np
from sklearn.cluster import KMeans
from skimage import io
from skimage.transform import rescale


def get_dominant_colour(img_url, debug=False):
    '''
    Get an image from a url, rescale it to save resources
    and then use Kmeans clustering to find the dominant colour
    and return it
    '''
    img = io.imread(img_url)
    shape = np.shape(img)

    if debug:
        print(f'Original shape: {np.shape(img)}')
    # Reshape to save memory for web
    if shape[0] > 1920 and shape[1] > 1080:
        img = rescale(img, 0.1, multichannel=True)
        img = img * 255
        if debug:
            print(f'x0.10 Scaled shape: {np.shape(img)}')
    img = img.reshape((-1, 3))
    if debug:
        print(f'Vectorised shape: {np.shape(img)}')

    cluster = KMeans(n_clusters=5, n_init=3, max_iter=10, tol=0.001)
    cluster.fit(img)

    labels = cluster.labels_
    centroid = cluster.cluster_centers_

    percent = []
    _, counts = np.unique(labels, return_counts=True)
    for i in range(len(centroid)):
        j = counts[i]
        j = j / (len(labels))
        percent.append(j)

    if debug:
        for i in range(len(centroid)):
            print(centroid[i], '{:0.2f}%'.format(percent[i] * 100))
    indices = np.argsort(percent)[::-1]
    dominant = centroid[indices[0]]

    return dominant


def clamp(x):
    '''
    Limits a number to the range of 0-255
    Converts floats to int
    '''
    return int(max(0, min(x, 255)))


def get_rgb_colour(img_url, debug=False):
    '''
    Calls get_dominant_colour on an image url and
    returns the r,g,b colour values limited to 0-255
    '''
    dominant_colour = get_dominant_colour(img_url, debug)
    r = dominant_colour[0]
    g = dominant_colour[1]
    b = dominant_colour[2]

    if debug:
        # Print the hex string
        hex_str = '#{0:02x}{1:02x}{2:02x}'.format(clamp(r), clamp(g), clamp(b))
        print(f'{hex_str}')

    rgb_colour = (clamp(r), clamp(g), clamp(b))

    return rgb_colour


def get_discord_colour(img_url, debug=False):
    '''
    Calls get_rgb_colour on an image url and converts the output
    to a discord colour object
    '''
    r, g, b = get_rgb_colour(img_url, debug)
    colour = discord.Colour.from_rgb(r, g, b)
    return colour
