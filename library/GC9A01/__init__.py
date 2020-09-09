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
import numbers
import time
import numpy as np

import spidev
import RPi.GPIO as GPIO


__version__ = '0.0.2'

BG_SPI_CS_BACK = 0
BG_SPI_CS_FRONT = 1

SPI_CLOCK_HZ = 16000000

# TODO: Complete this table
GC9A01_SLEEP_OUT = 0x11
GC9A01_DISPLAY_ON = 0x29
GC9A01_TEARING_EFFECT_LINE_ON = 0x35
GC9A01_MEMORY_ACCESS_CONTROL = 0x36
GC9A01_PIXEL_FORMAT_SET = 0x3A
GC9A01_DISPLAY_INVERSION_ON = 0x21

# These are compatible with GC9A01
ST7789_CASET = 0x2A
ST7789_RASET = 0x2B
ST7789_RAMWR = 0x2C
ST7789_RAMRD = 0x2E

class GC9A01(object):
    """Representation of an GC9A01 TFT LCD."""

    def __init__(self, port, cs, dc, backlight=None, rst=None, width=240,
                 height=240, rotation=90, invert=True, spi_speed_hz=4000000):
        """Create an instance of the display using SPI communication.

        Must provide the GPIO pin number for the D/C pin and the SPI driver.

        Can optionally provide the GPIO pin number for the reset pin as the rst parameter.

        :param port: SPI port number
        :param cs: SPI chip-select number (0 or 1 for BCM
        :param backlight: Pin for controlling backlight
        :param rst: Reset pin for GC9A01
        :param width: Width of display connected to GC9A01
        :param height: Height of display connected to GC9A01
        :param rotation: Rotation of display connected to GC9A01
        :param invert: Invert display
        :param spi_speed_hz: SPI speed (in Hz)

        """

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self._spi = spidev.SpiDev(port, cs)
        self._spi.mode = 0
        self._spi.lsbfirst = False
        self._spi.max_speed_hz = spi_speed_hz

        self._dc = dc
        self._rst = rst
        self._width = width
        self._height = height
        self._rotation = rotation
        self._invert = invert

        self._offset_left = 0
        self._offset_top = 0

        # Set DC as output.
        GPIO.setup(dc, GPIO.OUT)

        # Setup backlight as output (if provided).
        self._backlight = backlight
        if backlight is not None:
            GPIO.setup(backlight, GPIO.OUT)
            GPIO.output(backlight, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(backlight, GPIO.HIGH)

        # Setup reset as output (if provided).
        if rst is not None:
            GPIO.setup(rst, GPIO.OUT)

        self.reset()
        self._init()

    def send(self, data, is_data=True, chunk_size=4096):
        """Write a byte or array of bytes to the display. Is_data parameter
        controls if byte should be interpreted as display data (True) or command
        data (False).  Chunk_size is an optional size of bytes to write in a
        single SPI transaction, with a default of 4096.
        """
        # Set DC low for command, high for data.
        GPIO.output(self._dc, is_data)
        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start + chunk_size, len(data))
            self._spi.xfer(data[start:end])

    def set_backlight(self, value):
        """Set the backlight on/off."""
        if self._backlight is not None:
            GPIO.output(self._backlight, value)

    @property
    def width(self):
        return self._width if self._rotation == 0 or self._rotation == 180 else self._height

    @property
    def height(self):
        return self._height if self._rotation == 0 or self._rotation == 180 else self._width

    def command(self, data):
        """Write a byte or array of bytes to the display as command data."""
        self.send(data, False)

    def data(self, data):
        """Write a byte or array of bytes to the display as display data."""
        self.send(data, True)

    def reset(self):
        """Reset the display, if reset pin is connected."""
        if self._rst is not None:
            GPIO.output(self._rst, 1)
            time.sleep(0.500)
            GPIO.output(self._rst, 0)
            time.sleep(0.500)
            GPIO.output(self._rst, 1)
            time.sleep(0.500)

    def _init(self):
        # Initialize the display using the example sequence from sample code found at:
        # https://www.buydisplay.com/1-28-inch-tft-ips-lcd-display-module-240x240-spi-for-arduino-raspberry-pi 
        self.command(0xEF)
     
        self.command(0xEB)
        self.data(0x14) 
        
        self.command(0xFE)             
        self.command(0xEF) 

        self.command(0xEB)    
        self.data(0x14) 

        self.command(0x84)            
        self.data(0x40) 

        self.command(0x85)            
        self.data(0xFF) 

        self.command(0x86)            
        self.data(0xFF) 

        self.command(0x87)            
        self.data(0xFF)

        self.command(0x88)            
        self.data(0x0A)

        self.command(0x89)            
        self.data(0x21) 

        self.command(0x8A)            
        self.data(0x00) 

        self.command(0x8B)            
        self.data(0x80) 

        self.command(0x8C)            
        self.data(0x01) 

        self.command(0x8D)            
        self.data(0x01) 

        self.command(0x8E)            
        self.data(0xFF) 

        self.command(0x8F)            
        self.data(0xFF) 

        self.command(0xB6)
        self.data(0x00)           
        self.data(0x00) 
        
        # TODO: Set up rotation/mirroring correctly here
        USE_HORIZONTAL = 0
        mac_config = [0x18, 0x28, 0x48, 0x88]
        
        self.command(GC9A01_MEMORY_ACCESS_CONTROL)
        self.data(mac_config[USE_HORIZONTAL])

        self.command(GC9A01_PIXEL_FORMAT_SET)            
        self.data(0x05) 

        self.command(0x90)            
        self.data(0x08)
        self.data(0x08)
        self.data(0x08)
        self.data(0x08) 

        self.command(0xBD)            
        self.data(0x06)
        
        self.command(0xBC)            
        self.data(0x00)   

        self.command(0xFF)            
        self.data(0x60)
        self.data(0x01)
        self.data(0x04)

        self.command(0xC3)            
        self.data(0x13)
        self.command(0xC4)            
        self.data(0x13)

        self.command(0xC9)            
        self.data(0x22)

        self.command(0xBE)            
        self.data(0x11) 

        self.command(0xE1)            
        self.data(0x10)
        self.data(0x0E)

        self.command(0xDF)            
        self.data(0x21)
        self.data(0x0c)
        self.data(0x02)

        self.command(0xF0)   
        self.data(0x45)
        self.data(0x09)
        self.data(0x08)
        self.data(0x08)
        self.data(0x26)
        self.data(0x2A)

        self.command(0xF1)    
        self.data(0x43)
        self.data(0x70)
        self.data(0x72)
        self.data(0x36)
        self.data(0x37)  
        self.data(0x6F)

        self.command(0xF2)   
        self.data(0x45)
        self.data(0x09)
        self.data(0x08)
        self.data(0x08)
        self.data(0x26)
        self.data(0x2A)

        self.command(0xF3)   
        self.data(0x43)
        self.data(0x70)
        self.data(0x72)
        self.data(0x36)
        self.data(0x37) 
        self.data(0x6F)

        self.command(0xED)    
        self.data(0x1B) 
        self.data(0x0B) 

        self.command(0xAE)            
        self.data(0x77)
        
        self.command(0xCD)            
        self.data(0x63)       

        self.command(0x70)            
        self.data(0x07)
        self.data(0x07)
        self.data(0x04)
        self.data(0x0E) 
        self.data(0x0F) 
        self.data(0x09)
        self.data(0x07)
        self.data(0x08)
        self.data(0x03)

        self.command(0xE8)            
        self.data(0x34)

        self.command(0x62)            
        self.data(0x18)
        self.data(0x0D)
        self.data(0x71)
        self.data(0xED)
        self.data(0x70) 
        self.data(0x70)
        self.data(0x18)
        self.data(0x0F)
        self.data(0x71)
        self.data(0xEF)
        self.data(0x70) 
        self.data(0x70)

        self.command(0x63)            
        self.data(0x18)
        self.data(0x11)
        self.data(0x71)
        self.data(0xF1)
        self.data(0x70) 
        self.data(0x70)
        self.data(0x18)
        self.data(0x13)
        self.data(0x71)
        self.data(0xF3)
        self.data(0x70) 
        self.data(0x70)

        self.command(0x64)            
        self.data(0x28)
        self.data(0x29)
        self.data(0xF1)
        self.data(0x01)
        self.data(0xF1)
        self.data(0x00)
        self.data(0x07)

        self.command(0x66)            
        self.data(0x3C)
        self.data(0x00)
        self.data(0xCD)
        self.data(0x67)
        self.data(0x45)
        self.data(0x45)
        self.data(0x10)
        self.data(0x00)
        self.data(0x00)
        self.data(0x00)

        self.command(0x67)            
        self.data(0x00)
        self.data(0x3C)
        self.data(0x00)
        self.data(0x00)
        self.data(0x00)
        self.data(0x01)
        self.data(0x54)
        self.data(0x10)
        self.data(0x32)
        self.data(0x98)

        self.command(0x74)            
        self.data(0x10)   
        self.data(0x85)   
        self.data(0x80)
        self.data(0x00) 
        self.data(0x00) 
        self.data(0x4E)
        self.data(0x00)                   
        
        self.command(0x98)            
        self.data(0x3e)
        self.data(0x07)

        self.command(GC9A01_TEARING_EFFECT_LINE_ON)  

        self.command(GC9A01_DISPLAY_INVERSION_ON)

        self.command(GC9A01_SLEEP_OUT)
        time.sleep(0.120)

        self.command(GC9A01_DISPLAY_ON)
        time.sleep(0.020)




    def begin(self):
        """Set up the display

        Deprecated. Included in __init__.

        """
        pass

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to width-1,height-1.
        """
        if x1 is None:
            x1 = self._width - 1

        if y1 is None:
            y1 = self._height - 1

        y0 += self._offset_top
        y1 += self._offset_top

        x0 += self._offset_left
        x1 += self._offset_left

        self.command(ST7789_CASET)       # Column addr set
        self.data(x0 >> 8)
        self.data(x0 & 0xFF)             # XSTART
        self.data(x1 >> 8)
        self.data(x1 & 0xFF)             # XEND
        self.command(ST7789_RASET)       # Row addr set
        self.data(y0 >> 8)
        self.data(y0 & 0xFF)             # YSTART
        self.data(y1 >> 8)
        self.data(y1 & 0xFF)             # YEND
        self.command(ST7789_RAMWR)       # write to RAM

    def display(self, image):
        """Write the provided image to the hardware.

        :param image: Should be RGB format and the same dimensions as the display hardware.

        """
        # Set address bounds to entire display.
        self.set_window()
        # Convert image to array of 18bit 666 RGB data bytes.
        # Unfortunate that this copy has to occur, but the SPI byte writing
        # function needs to take an array of bytes and PIL doesn't natively
        # store images in 18-bit 666 RGB format.
        pixelbytes = list(self.image_to_data(image, self._rotation))
        # Write data to hardware.
        for i in range(0, len(pixelbytes), 4096):
            self.data(pixelbytes[i:i + 4096])

    def image_to_data(self, image, rotation=0):
        """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
        # NumPy is much faster at doing this. NumPy code provided by:
        # Keith (https://www.blogger.com/profile/02555547344016007163)
        pb = np.rot90(np.array(image.convert('RGB')), rotation // 90).astype('uint8')

        result = np.zeros((self._width, self._height, 2), dtype=np.uint8)
        result[..., [0]] = np.add(np.bitwise_and(pb[..., [0]], 0xF8), np.right_shift(pb[..., [1]], 5))
        result[..., [1]] = np.add(np.bitwise_and(np.left_shift(pb[..., [1]], 3), 0xE0), np.right_shift(pb[..., [2]], 3))
        return result.flatten().tolist()
