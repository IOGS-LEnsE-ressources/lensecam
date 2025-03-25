"""Example of pypylon library usage

    Tested with Basler a2A 1920-160ucBAS camera


@see https://github.com/basler/pypylon
@see https://github.com/basler/pypylon-samples/blob/main/notebooks/grabstrategies.ipynb
"""

from pypylon import pylon
import time
import numpy as np
from matplotlib import pyplot as plt

# Open first camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Set AOI
w = 400
y0 = (1936 // 2) - (w // 2)
x0 = (1216 // 2) - (w // 2)

# Set Color mode
color_mode = "Mono12"
# Exposure
exposure = 1000000
# Black Level
black_level = 10

# UPDATE PARAMETERS
camera.Open()
camera.UserSetSelector = "Default"
camera.UserSetLoad.Execute()
time.sleep(0.2)
camera.Width.SetValue(w)
camera.Height.SetValue(w)
camera.OffsetX.SetValue(x0)
camera.OffsetY.SetValue(y0)
camera.PixelFormat = color_mode
camera.ExposureTime.SetValue(exposure)
camera.Gamma.Value = 1.0
camera.GainAuto.Value = "Off"
camera.ExposureAuto.Value = "Off"
camera.BslColorSpace.Value = "Off"
camera.BalanceWhiteAuto.Value = "Off"
camera.BslLightSourcePresetFeatureEnable.Value = False
camera.LUTEnable.SetValue(False)

camera.BslBrightness.Value = 0
# Set the contrast mode to Linear
camera.BslContrastMode.Value = "Linear"
camera.BslContrast.Value = 0

camera.BslAcquisitionStopMode.Value = "AbortExposure"
# Enable Balance White Auto for the auto function ROI selected
camera.AutoFunctionROIUseWhiteBalance.Value = False
# Enable the 'Brightness' auto function (Gain Auto + Exposure Auto)
# for the auto function ROI selected
camera.AutoFunctionROIUseBrightness.Value = False
# Highlight the auto function ROI selected
camera.AutoFunctionROIHighlight.Value = False

camera.BslColorAdjustmentEnable = False

camera.BlackLevel.SetValue(black_level)
camera.BlackLevelSelector.Value = "All"

time.sleep(0.2)

print(f'FPS = {camera.ResultingFrameRate.Value}')

def get_image(camera, numberOfImagesToGrab=1):
    print(f'Expo = {camera.ExposureTime.GetValue()}')
    camera.StartGrabbingMax(numberOfImagesToGrab)
    images = []

    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Access the image data.
            img = grabResult.Array
            print(f'Shape : {img.shape}')
            images.append(img.copy())
        grabResult.Release()

    return images

# Test image
camera.ExposureTime.SetValue(200)
time.sleep(0.1)
print(f'FPS = {camera.ResultingFrameRate.Value}')
time.sleep(0.1)
images = get_image(camera, 1)


# Test with different exposure time
expo_time_list = [20, 20000, 100000, 250000, 500000, 1000000, 1500000, 2000000]
mean_value = []
stddev_value = []

for expo_time in expo_time_list:
    print(expo_time)
    camera.ExposureTime.SetValue(expo_time)
    time.sleep(0.1)
    print(f'FPS = {camera.ResultingFrameRate.Value}')
    time.sleep(0.1)
    images = get_image(camera, 1)

    print(images[0].dtype)
    m_v = np.mean(images)
    std_v = np.std(images)
    mean_value.append(m_v)
    stddev_value.append(std_v)

expo_times = np.array(expo_time_list)
mean_value = np.array(mean_value)
print(f'M0 = {mean_value[0]}')
#mean_value = mean_value - mean_value[0]

plt.figure()
plt.plot(expo_times, mean_value)
plt.title('Mean value of intensity')
'''
plt.figure()
plt.plot(expo_times, np.array(stddev_value))
plt.title('Standard deviation value of intensity')
'''
plt.show()

camera.Close()