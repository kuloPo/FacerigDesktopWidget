import pygame
import numpy as np
import cv2
import os
from configparser import ConfigParser

import gui

def find_all_camera():
    valid_cams = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap != None and cap.isOpened():
            valid_cams.append(i)
            cap.release()
    return valid_cams

def convert_transparent(frame):
    sensitivity = config.getint('main', 'sensitivity')
    green = np.array([0,255,0])
    mask = np.sum((frame-green)**2,axis=-1) < sensitivity**2
    frame[mask] = green

def update_setting():
    ScreenWidth, ScreenHeight, VideoWidth, VideoHeight = geometry
    # update stream
    global camera
    if int(menu_obj[0].get()) != config.getint('main', 'DeviceIndex'):
        DeviceIndex = int(menu_obj[0].get())
        config.set('main', 'DeviceIndex', str(DeviceIndex))
        camera.release()
        camera = cv2.VideoCapture(DeviceIndex)
    # update location
    X_AxisOffset = menu_obj[1].get()
    Y_AxisOffset = menu_obj[2].get()
    x_pos = ScreenWidth // 3 * 2 + X_AxisOffset
    y_pos = ScreenHeight-VideoHeight + Y_AxisOffset
    config.set('main', 'X_AxisOffset', str(X_AxisOffset))
    config.set('main', 'Y_AxisOffset', str(Y_AxisOffset))
    gui.update_location(hwnd, (x_pos, y_pos), geometry)
    # update sensitivity
    sensitivity = menu_obj[3].get()
    config.set('main', 'sensitivity', str(sensitivity))
    save_config(config)

def read_config():
    config_dir = os.path.expandvars(r'%LOCALAPPDATA%\FacefigDesktopWidget')
    config_path = os.path.expandvars(r'%LOCALAPPDATA%\FacefigDesktopWidget\config.ini')
    config = ConfigParser()
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)
    if config.read(config_path) == []:
        config.add_section('main')
        config.set('main', 'DeviceIndex', '1')
        config.set('main', 'X_AxisOffset', '0')
        config.set('main', 'Y_AxisOffset', '0')
        config.set('main', 'sensitivity', '150')
        save_config(config)
    return config

def save_config(config):
    config_path = os.path.expandvars(r'%LOCALAPPDATA%\FacefigDesktopWidget\config.ini')
    with open(config_path, 'w') as f:
        config.write(f)

def on_close():
    global running
    running = False
    pygame.quit()

if __name__ == '__main__':
    camera_list = find_all_camera()
    config = read_config()
    camera = cv2.VideoCapture(config.getint('main', 'DeviceIndex'))
    geometry = gui.get_geometry(camera)
    hwnd, display = gui.main_window_setup(config, geometry)
    menu, menu_obj = gui.menu_setup(config, camera_list, update_setting, on_close)
    running = True
    while running:
        _, frame = camera.read()                                  # get stream by frame
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE) # rotate the frame 90 degree counterclockwise
        RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)              # covert BGR to RGB
        convert_transparent(RGB)                                  # change all similar to green to exact green
        try:
            pygame.surfarray.blit_array(display, RGB)
        except ValueError: # happen when switch stream
            pass
        pygame.display.flip()
        menu.update()
        cv2.waitKey(1)
        if running and pygame.QUIT in [event.type for event in pygame.event.get()]:
            pygame.quit()
            camera.release()
            running = False
