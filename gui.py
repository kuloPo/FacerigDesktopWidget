import pygame
import tkinter
from tkinter import ttk
import win32api
import win32con
import win32gui
import os

def get_geometry(camera):
    ScreenWidth = win32api.GetSystemMetrics(0)
    ScreenHeight = win32api.GetSystemMetrics(1)
    VideoWidth = int(camera.get(3))
    VideoHeight = int(camera.get(4))
    return ScreenWidth, ScreenHeight, VideoWidth, VideoHeight

def main_window_setup(config, geometry):
    ScreenWidth, ScreenHeight, VideoWidth, VideoHeight = geometry
    pygame.init()
    X_AxisOffset = config.getint('main', 'X_AxisOffset')
    Y_AxisOffset = config.getint('main', 'Y_AxisOffset')
    x_pos = ScreenWidth // 3 * 2 + X_AxisOffset
    y_pos = ScreenHeight-VideoHeight + Y_AxisOffset
    # set window position
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (x_pos, y_pos)
    # launch the window with no frame
    display = pygame.display.set_mode((VideoWidth, VideoHeight),pygame.NOFRAME)
    # get handle
    hwnd = pygame.display.get_wm_info()["window"]
    # window transparent and click pass through
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW)
    # set transparent color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,255,0), 0, win32con.LWA_COLORKEY)
    # set window always on top
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x_pos, y_pos, VideoWidth, VideoHeight, win32con.SWP_NOMOVE |\
        win32con.SWP_NOACTIVATE| win32con.SWP_NOOWNERZORDER | win32con.SWP_SHOWWINDOW)
    return hwnd, display

def menu_setup(config, camera_list, button_func, on_close):
    root = tkinter.Tk()
    root.geometry('250x250')
    root.resizable(width=False, height=False)
    root.title('Facefig Desktop Widget')
    root.protocol("WM_DELETE_WINDOW",  on_close)

    camera_label = tkinter.Label(root, text='stream: ', font=("Arial", 12))
    camera_box = ttk.Combobox(root)
    camera_box['value'] = camera_list
    camera_label.grid(row = 0, column = 0, padx=5, pady=5, sticky=tkinter.W)
    camera_box.grid(row = 0, column = 1, padx=5, pady=5, sticky=tkinter.W)

    x_label = tkinter.Label(root, text='X offset: ', font=("Arial", 12))
    x_scale = tkinter.Scale(root, from_=-500, to=500, orient=tkinter.HORIZONTAL)
    x_label.grid(row = 1, column = 0, padx=5, pady=5, sticky=tkinter.W)
    x_scale.grid(row = 1, column = 1, padx=5, pady=5, sticky=tkinter.W)

    y_label = tkinter.Label(root, text='Y offset: ', font=("Arial", 12))
    y_scale = tkinter.Scale(root, from_=-250, to=250, orient=tkinter.HORIZONTAL)
    y_label.grid(row = 2, column = 0, padx=5, pady=5, sticky=tkinter.W)
    y_scale.grid(row = 2, column = 1, padx=5, pady=5, sticky=tkinter.W)

    sensitivity_label = tkinter.Label(root, text='sensitivity: ', font=("Arial", 12))
    sensitivity_scale = tkinter.Scale(root, from_=0, to=500, orient=tkinter.HORIZONTAL)
    sensitivity_label.grid(row = 3, column = 0, padx=5, pady=5, sticky=tkinter.W)
    sensitivity_scale.grid(row = 3, column = 1, padx=5, pady=5, sticky=tkinter.W)

    confirm_button = tkinter.Button(root, text="Confirm", command=button_func)
    confirm_button.grid(row=4, padx=15, pady=5, columnspan=2, sticky=tkinter.W+tkinter.E)

    camera_box.current(config.getint('main', 'DeviceIndex'))
    x_scale.set(config.getint('main', 'X_AxisOffset'))
    y_scale.set(config.getint('main', 'Y_AxisOffset'))
    sensitivity_scale.set(config.getint('main', 'sensitivity'))

    return root, (camera_box, x_scale, y_scale, sensitivity_scale)

def update_location(hwnd, pos, geometry):
    x_pos, y_pos = pos
    ScreenWidth, ScreenHeight, VideoWidth, VideoHeight = geometry
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x_pos, y_pos, VideoWidth, VideoHeight, 0)
