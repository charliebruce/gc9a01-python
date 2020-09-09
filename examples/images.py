# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import time
from PIL import Image
import GC9A01 as GC9A01
from os import listdir
from os.path import isfile, join

print("""
image.py - Display an image on the LCD.

If you're using Breakout Garden, plug the 1.3" LCD (SPI)
breakout into the rear slot.
""")

if len(sys.argv) < 2:
    print("Usage: {} <folder containing images> <seconds to delay> <loop>".format(sys.argv[0]))
    sys.exit(1)

image_folder = sys.argv[1]
delay = float(sys.argv[2])
loop = True if sys.argv[3] in ["yes", "true", "True", "1"] else False

# Create GC9A01 LCD display class.
disp = GC9A01.GC9A01(
    port=0,
    cs=GC9A01.BG_SPI_CS_BACK,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=9,
    rst=24,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000
)

WIDTH = disp.width
HEIGHT = disp.height

image_files = [join(image_folder, f) for f in listdir(image_folder) if isfile(join(image_folder, f)) and ".png" in f and not f.startswith(".")]

# Load an image.
print('Loading {} images...'.format(len(image_files)))

images = [Image.open(image_file) for image_file in sorted(image_files)]

# Resize the image
images = [image.resize((WIDTH, HEIGHT)) for image in images]

# Draw the image on the display hardware.
print('Drawing images...')

# Initialize display.
disp.begin()

# Display all the images in order, delaying and looping if requested
running = True
while(running):
    for image in images:
        disp.display(image)
        time.sleep(delay)
    if not loop:
        running = False
