import pygame
import numpy as np
import cv2
import win32api
import win32con
import win32gui
import os
import re

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
            pygame.surfarray.blit_array(self.display, RGB)
            pygame.display.flip()
            cv2.waitKey(1)

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
