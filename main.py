import pygame
import tkinter
import numpy as np
import cv2
import win32api
import win32con
import win32gui
import os
import re

def main_window_setup():
    ScreenWidth = win32api.GetSystemMetrics(0)
    ScreenHeight = win32api.GetSystemMetrics(1)
    VideoWidth = int(camera.get(3))
    VideoHeight = int(camera.get(4))
    pygame.init()
    # set window position
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (ScreenWidth // 3 * 2 + X_AxisOffset,ScreenHeight-VideoHeight + Y_AxisOffset)
    # launch the window with no frame
    display = pygame.display.set_mode((VideoWidth, VideoHeight),pygame.NOFRAME)
    # get handle
    hwnd = pygame.display.get_wm_info()["window"]
    # window transparent and click pass through
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    # set transparent color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*TransparentColor), 0, win32con.LWA_COLORKEY)
    # set window always on top
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, VideoWidth, VideoHeight, win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE| win32con.SWP_NOOWNERZORDER|win32con.SWP_SHOWWINDOW)
    return hwnd, display

def ConvertTransparent(frame):
    green = np.array([0,255,0])
    mask = np.sum((frame-green)**2,axis=-1) < 200**2
    frame[mask] = green

def ReadConfig():
    # todo
    content = []
    with open('config.txt') as f:
        for n in range(4):
            content.append(re.search(r'=(.+?) ',f.readline()).group(1))
    TransparentColor = content[0].split(',')
    for n in range(3):
        TransparentColor[n] = int(TransparentColor[n])
    DeviceIndex = int(content[1])
    X_AxisOffset = int(content[2])
    Y_AxisOffset = int(content[3])
    return TransparentColor, DeviceIndex, X_AxisOffset, Y_AxisOffset

if __name__ == '__main__':
    TransparentColor, DeviceIndex, X_AxisOffset, Y_AxisOffset = ReadConfig()
    camera = cv2.VideoCapture(DeviceIndex)
    hwnd, display = main_window_setup()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        _, frame = camera.read()
        frame = np.transpose(frame,(1,0,2))
        RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ConvertTransparent(RGB)
        pygame.surfarray.blit_array(display, RGB)
        pygame.display.flip()
        cv2.waitKey(1)
