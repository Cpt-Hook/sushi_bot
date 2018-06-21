import os

import numpy
import pyscreenshot as ImageGrab
from PIL import ImageOps, Image

x_pad = 465
y_pad = 246
width = 640
height = 480

table_coords = (
    (33, 56, 80, 83),
    (134, 56, 181, 83),
    (235, 56, 282, 83),
    (336, 56, 383, 83),
    (437, 56, 484, 83),
    (538, 56, 585, 83))
food_sums = {2232: 'onigiri', 2876: 'california', 2239: 'gunkan', 2207: 'salmonroll', 2654: 'shrimpsushi',
             2455: 'unagiroll'}

next_level_coords = (183, 365, 424, 390)
next_level_sum = 6651

window_sample = Image.open("window_sample.png")


def set_window_coords():
    global x_pad, y_pad

    screenshot = ImageGrab.grab()
    screenshot = ImageOps.grayscale(screenshot)

    arr_h = numpy.asarray(screenshot)
    arr_n = numpy.asarray(window_sample)

    y_h, x_h = arr_h.shape[:2]
    y_n, x_n = arr_n.shape[:2]

    xstop = x_h - x_n + 1
    ystop = y_h - y_n + 1

    check = xstop // 10
    percentage = 0
    for xmin in range(0, xstop):
        if (xmin % check) == 0:
            print(f"{percentage}%")
            percentage += 10
        for ymin in range(0, ystop):
            xmax = xmin + x_n
            ymax = ymin + y_n

            arr_s = arr_h[ymin:ymax, xmin:xmax]
            arr_t = (arr_s == arr_n)
            if arr_t.all():
                x_pad = xmin
                y_pad = ymin
                return True
    return False


def grab_screen():
    """Gives pixel exact screenshot of https://www.miniclip.com/games/sushi-go-round/en/ game.
       Google chrome, 100% zoom, fullHD display
       Cookie bar at the top needs to be canceled."""
    return ImageGrab.grab((x_pad, y_pad, x_pad + width, y_pad + height))


def screen_save(name="sushi_screen"):
    image = grab_screen()
    file_path = os.getcwd() + "\\" + name + ".png"
    image.save(file_path, "PNG")
    print(f"Screen saved in {file_path}")


def get_requests():
    orders = []
    img = grab_screen()
    img = ImageOps.grayscale(img)

    for coords in table_coords:
        cropped_img = img.crop(coords)
        color_sum = numpy.array(cropped_img.getcolors()).sum()
        orders.append(food_sums.get(color_sum))
    return orders


def level_ended():
    img = grab_screen()
    img = ImageOps.grayscale(img)
    cropped_img = img.crop(next_level_coords)
    return numpy.array(cropped_img.getcolors()).sum() == next_level_sum


def get_food_sums():
    sums = []
    img = grab_screen()
    img = ImageOps.grayscale(img)
    for coords in table_coords:
        cropped_img = img.crop(coords)
        color_sum = numpy.array(cropped_img.getcolors()).sum()
        sums.append((coords, color_sum))
    return sums


if __name__ == '__main__':
    set_window_coords()
