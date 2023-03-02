import cv2
import numpy as np


def encode(source, amplitudeResolution, angularResolution, isCircular, bitmap=False):
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


def toBitmap(image, bigEndian=True, serial=2):
    if(image.shape[1] % serial != 0):
        print(f"image shape {image.shape} is not serializable with {serial}")
        return
    bits = np.array([[[list('{0:08b}'.format(num))
                    for num in color] for color in row] for row in image])
    # Convert the bits to integers and reshape to 3D
    result = bits.astype(int).reshape(
        (image.shape[0], image.shape[1], image.shape[2], -1))
    print(result.shape)
    bitmap = []
    order = [1, 0, 2]
    for i, row in enumerate(result):
        if (i < len(result)-1):
            continue
        registers = []
        for j in range(result.shape[1]):
            print(f"{row[j][0]} {row[j][1]} {row[j][2]}")

        for k in order:
            arr = np.arange(result.shape[1]//serial)
            if bigEndian:
                arr = np.arange(result.shape[1]//serial-1, -1, -1)
            for s in range(serial):
                [registers.append(np.dot(row[s::serial, k, x], 2 ** arr))
                    for x in range(7)]
        bitmap.append(np.array(registers))
        print(np.array(registers))
    return bitmap


source = cv2.imread("kul.png")
encode(source, 6, 3, True, True)
