import PictureEncoder
import cv2
import numpy as np
from time import sleep

# cv2.imshow("Image", source)

# cv2.imshow("Polar Image", polar_image)
# cv2.imshow("Encoded Image", encodedImage)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
maxAmp = 50
angleSlices = 200
ledSize = 1
offset = 0
im = cv2.imread("thomas more.png")
polar = PictureEncoder.encode(im, maxAmp, angleSlices, False)
cv2.imwrite("polar.jpg", polar)
print(polar)
# cv2.imshow("Encoded Image", polar)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


def pol2cart(rho, phi):
    x = int(rho * np.cos(phi))
    y = int(rho * np.sin(phi))
    return(x, y)


def resize(img, scale=1):
    dim = img.shape[0]*scale
    return cv2.resize(img, (dim, dim), interpolation=cv2.INTER_AREA)


scale = 20
dim = (maxAmp*scale, maxAmp*scale, 3)
canvas = np.zeros(dim)
center = canvas.shape[0]//2
rho = center
phi = 0
phiScale = angleSlices/(np.pi*2)
print(f"amp: {maxAmp}")
print(f"ang: {angleSlices}")
while True:
    angle = int(np.round(phiScale*phi))
    for i in range(1+offset, maxAmp):
        x, y = pol2cart((center/maxAmp)*i, phi)

        color = (
            polar[int(min(np.round(phiScale*phi), angleSlices-1)), i]/255).tolist()
        print(f"ang: {angle}, amp: {i}, color: {color}")
        canvas = cv2.circle(canvas, (x+center, y+center),
                            ledSize, color, -1)
    cv2.imshow("Original", resize(canvas, 1))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    phi += 0.02
    if phi >= np.pi*2-0.0001:
        phi = 0
        canvas = np.zeros(dim)
    # sleep(0.001)
