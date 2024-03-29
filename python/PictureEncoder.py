import cv2
import numpy as np
import json


def encode(source, amplitudeResolution=98, angularResolution=50, isCircular=True, bitmap=False):
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

    if not bitmap:
        return encodedImage
    return toBitmap(encodedImage)


def transform2Poles(source, isCircular):
    """high resolution transform to poles

    Args:
        source (np.array): Image
        isCircular (Boolean): whether image is circle or rectangle

    Returns:
        polar image: image X-axis=Amplitude, y-axis= Polar Value
    """
    img = source.astype(np.float32)
    length = max(img.shape[0], img.shape[1])/2
    center = (img.shape[0]/2,
              img.shape[1]/2)
    if isCircular:
        value = length
    else:
        value = np.sqrt(((length)**2.0)+((length)**2.0))

    polar_image = cv2.linearPolar(
        img, center, value,
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


def toBitmap(image, serial=7):
    """transforms image to a format wich is easily read by the esp

    Args:
        image (np.array): Image
        serial (int): amount of leds in serie on the pov display

    Returns:
        List(List(int)): Bitmap 2D list of registe value
    """
    assert image.shape[1] % serial == 0, f"image shape {image.shape} is not serializable with {serial}"
    bits = np.array([[[list('{0:08b}'.format(num))
                    for num in color] for color in row] for row in image])

    # Convert the bits to integers and reshape to 3D
    result = bits.astype(np.int64)
    bitmap = []
    color_order = [0, 1, 2]
    custom_arr = np.array(
        [12, 13, 14, 15, 16, 11, 10, 9, 8, 7, 6, 5, 4, 2])
    arr = np.flip(custom_arr)
    assert arr.shape[0] == image.shape[
        1]//serial, f"size of register index({arr.shape[0]}) is not size of parralel leds({image.shape[1]//serial})"
    for i, row in enumerate(result):
        registers = []
        for j in range(result.shape[1]):
            pass
        for s in range(serial):
            for k in color_order:
                [(registers.append(np.dot(row[s::serial, k, x], 2 ** arr)))
                 for x in range(8)]
        bitmap.append(registers)
    np.savetxt(f'array_{len(bitmap)}.txt', bitmap, fmt='%d', delimiter=',',
               newline='},\n{', header=f'uint32_t image[{len(bitmap)}][{7*8*3}] = ' + '{\n', footer='};')
    return bitmap


def main():
    ROTATE = True
    BITMAP_ONLY = False
    CIRCLE_IMG = True
    SLICES = 500  # angular resolution
    image = cv2.imread("kul.png")

    if ROTATE:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    if BITMAP_ONLY:
        toBitmap(image, bigEndian=True, custom=True, serial=7)
    else:
        encode(image, angularResolution=SLICES,
               isCircular=CIRCLE_IMG, bitmap=True)


main()
