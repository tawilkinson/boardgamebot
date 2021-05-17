import discord
import logging
import numpy as np
from cachetools import cached, TTLCache
from sklearn.cluster import KMeans
from skimage import io
from skimage.transform import rescale

logger = logging.getLogger('discord')


def get_dominant_colour(img_url):
    '''
    Get an image from a url, rescale it to save resources
    and then use Kmeans clustering to find the dominant colour
    and return it
    '''
    img = io.imread(img_url)
    shape = np.shape(img)

    if logger.level >= 10:
        logger.debug(f'>>> Original shape: {np.shape(img)}')
    # Reshape to save memory for web
    if shape[0] > 1920 and shape[1] > 1080:
        img = rescale(img, 0.1, multichannel=True, anti_aliasing=False)
        img = img * 255
        if logger.level >= 10:
            logger.debug(f'>>> x0.10 Scaled shape: {np.shape(img)}')
    img = img.reshape((-1, 3))
    if logger.level >= 10:
        logger.debug(f'>>> Vectorised shape: {np.shape(img)}')

    cluster = KMeans(n_clusters=5, n_init=3, max_iter=10, tol=0.001)
    cluster.fit(img)

    labels = cluster.labels_
    centroid = cluster.cluster_centers_

    percent = []
    _, counts = np.unique(labels, return_counts=True)
    for count, _ in enumerate(centroid):
        j = counts[count]
        j = j / (len(labels))
        percent.append(j)

    if logger.level >= 10:
        for count, value in enumerate(centroid):
            logger.debug(f'{value} {percent[count] * 100} %')
    indices = np.argsort(percent)[::-1]
    dominant = centroid[indices[0]]

    return dominant


def clamp(x):
    '''
    Limits a number to the range of 0-255
    Converts floats to int
    '''
    return int(max(0, min(x, 255)))


def get_rgb_colour(img_url):
    '''
    Calls get_dominant_colour on an image url and
    returns the r,g,b colour values limited to 0-255
    '''
    dominant_colour = get_dominant_colour(img_url)
    r = dominant_colour[0]
    g = dominant_colour[1]
    b = dominant_colour[2]

    if logger.level >= 10:
        # Print the hex string
        hex_str = '#{0:02x}{1:02x}{2:02x}'.format(clamp(r), clamp(g), clamp(b))
        logger.debug(f'{hex_str}')

    rgb_colour = (clamp(r), clamp(g), clamp(b))

    return rgb_colour


@cached(cache=TTLCache(maxsize=1024, ttl=86400))
def get_discord_colour(img_url):
    '''
    Calls get_rgb_colour on an image url and converts the output
    to a discord colour object
    '''
    r, g, b = get_rgb_colour(img_url)
    colour = discord.Colour.from_rgb(r, g, b)
    return colour
