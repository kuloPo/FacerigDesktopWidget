import pygame
import numpy as np
import cv2
import win32api
import win32con
import win32gui
import os
import re
from math import sqrt

class FacerigDesktopWidget:
    def __init__(self):
        TransparentColor, DeviceIndex, X_AxisOffset, Y_AxisOffset = self._ReadConfig()
        ScreenWidth = win32api.GetSystemMetrics(0)
        ScreenHeight = win32api.GetSystemMetrics(1)
        self.camera = cv2.VideoCapture(DeviceIndex)
        VideoWidth = int(self.camera.get(3))
        VideoHeight = int(self.camera.get(4))
        os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (ScreenWidth // 3 * 2 + X_AxisOffset,ScreenHeight-VideoHeight + Y_AxisOffset)
        pygame.init()
        self.display = pygame.display.set_mode((VideoWidth, VideoHeight),pygame.NOFRAME)
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*TransparentColor), 0, win32con.LWA_COLORKEY)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, VideoWidth, VideoHeight, win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE| win32con.SWP_NOOWNERZORDER|win32con.SWP_SHOWWINDOW)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            _, frame = self.camera.read()
            frame = np.transpose(frame,(1,0,2))
            RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            RGB = self._ConvertTransparent(RGB)
            pygame.surfarray.blit_array(self.display, RGB)
            pygame.display.flip()
            cv2.waitKey(1)

    def _ConvertTransparent(self,frame):
        green = np.array([0,255,0])
        mask = np.sum((frame-green)**2,axis=-1) < 150**2
        frame[mask] = green
        return frame

    '''
    def _ConvertTransparent(self,frame):
        w,h,_ = frame.shape
        for x in range(w):
            for y in range(h):
                r,g,b=list(frame[x][y])
                r = int(r)
                g = int(g)
                b = int(b)
                if self._ColorDistance(r,g,b):
                    frame[x][y][0] = 0
                    frame[x][y][1] = 255
                    frame[x][y][2] = 0
        return frame

    def _ColorDistance(self,r,g,b):
        if sqrt(r*r+(g-255)*(g-255)+b*b) < 200:
            return True
    '''

    def _ReadConfig(self):
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
    FacerigDesktopWidget().run()
