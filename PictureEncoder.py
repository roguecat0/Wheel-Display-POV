import cv2
import numpy as np
import json


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


def toBitmap(image, bigEndian=True, custom=True, serial=2):
    assert image.shape[1] % serial == 0, f"image shape {image.shape} is not serializable with {serial}"
    bits = np.array([[[list('{0:08b}'.format(num))
                    for num in color] for color in row] for row in image])
    print(bits)

    # Convert the bits to integers and reshape to 3D
    result = bits.astype(np.int64).reshape(
        (image.shape[0], image.shape[1], image.shape[2], -1))
    print(result.shape)
    print(result)
    bitmap = []
    color_order = [0, 1, 2]  # [1, 0, 2]
    custom_arr = np.array(
        [2, 4, 16, 17, 5, 18, 19, 20, 21, 22, 23, 27, 26, 25])
    for i, row in enumerate(result):
        registers = []
        # if (i < len(result)-1):
        #     continue
        
        for j in range(result.shape[1]):
            pass
            # print(f"{row[j][0]} {row[j][1]} {row[j][2]}")

        for k in color_order:
            arr = np.arange(result.shape[1]//serial)
            if bigEndian:
                arr = np.arange(result.shape[1]//serial-1, -1, -1)
            if custom:
                arr = custom_arr#[:2]
                assert arr.shape[0] == image.shape[
                    1]//serial, f"size of register index({arr.shape[0]}) is not size of parralel leds({image.shape[1]//serial})"
            for s in range(serial):
                [registers.append(np.dot(row[s::serial, k, x], 2 ** arr))
                    for x in range(8)]
        bitmap.append(registers)
        # print(np.array(registers).shape)
        # print(np.array(registers))
        # print(custom_arr[:2])
        # print(np.array([x for x in range(max(custom_arr[:2])+1)]))
        # print(np.array([2**x for x in range(max(custom_arr[:2])+1)]))

    return bitmap


# source = cv2.imread("kul.png")
# encode(source, 2, 3, True, True)
def calc(tot_leds, aantal_pinne, freq, aspect):

    ser_leds = int(np.round(tot_leds/aantal_pinne))

    tot_leds = ser_leds*aantal_pinne
    print(f"Aantal Leds {tot_leds}")
    slices = int(2*np.pi*tot_leds / aspect)
    print(f"Aantal Slices {slices}")
    return (ser_leds*32+64)*freq*slices


# print(f"{calc(tot_leds=14, aantal_pinne=14, freq=10, aspect=3)/1000} Kbps \nMax = 500 Kbps")
lol = encode(cv2.imread("kul.png"),50,100,True,True)
with open("98_leds_100_slices_7_para.txt","w") as f:
    f.write(str(lol))
print("[")
for i,v in enumerate(lol):
    print(v,end=",\n")
print("]")
print(len(lol))
print(len(lol[0]))
