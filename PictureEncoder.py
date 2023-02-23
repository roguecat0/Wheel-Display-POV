import cv2
import numpy as np


def encode(source, amplitudeResolution, angularResolution, isCircular):
    """ Takes an image and returns the Polar 
    representation with the preffered 
    amplitude and angular dimensions
    Args:
        source (np.array): Image
        amplitudeResolution (Int): Number of leds
        angularResolution (Int): pixel shift per Unit turned
        isCircular (Boolean): whether its a circlular or rectangular image

    Returns:
        np.array: Image with polar axises
    """
    polar_image = transform2Poles(source, isCircular)
    encodedImage = setResolution(
        polar_image, amplitudeResolution, angularResolution)
    return encodedImage


def transform2Poles(source, isCircular):
    """high resolution transform to poles

    Args:
        source (np.array): Image
        isCircular (Boolean): whether image is circle or rectangle

    Returns:
        polar image: image X-axis=Amplitude, y-axis= Polar Value
    """
    img = source.astype(np.float32)
    if isCircular:
        value = max(img.shape[0], img.shape[1])/2
    else:
        value = np.sqrt(((img.shape[0]/2.0)**2.0)+((img.shape[1]/2.0)**2.0))

    polar_image = cv2.linearPolar(
        img, (img.shape[0]/2,
              img.shape[1]/2), value,
        cv2.WARP_FILL_OUTLIERS
    )
    polar_image = polar_image.astype(np.uint8)
    return polar_image


def setResolution(image, amplitudeResolution, AngularResolution):
    """sets the amplitude and angular resolution of the image

    Args:
        image (np.array): Image
        amplitudeResolution (Int): Number of leds
        AngularResolution (Int): pixel shift per Unit turned

    Returns:
        np.array: resized polar image
    """
    newDim = (amplitudeResolution, AngularResolution)
    resizedImg = cv2.resize(image, newDim, interpolation=cv2.INTER_AREA)
    return resizedImg
