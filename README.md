# rgb565-converter

*This is TheStumbler fork, see below*

[![CI](https://github.com/CommanderRedYT/rgb565-converter/actions/workflows/ci.yaml/badge.svg)](https://github.com/CommanderRedYT/rgb565-converter/actions/workflows/ci.yaml)

A simple script to help converting png files to rgb565 (used in [TFT_eSPI](https://github.com/Bodmer/TFT_eSPI))


## Install
```bash
# Then, install the package
pip install rgb565-converter
# or
pip3 install rgb565-converter
```

## The Stumbler's Branch

While doing some experiments displaying images on TFT using MicroPython,
I found this rgb565 converter. It didn't exactly do what I needed, so I
started changing it.

* Added byte vs word output options
* Option to generate Python output vs C++
* Added crude handling of RGB/RGBA and 4-bit grayscale. 
* Changed the way output hex was built, string-wise to list-wise
* Completely ignored the reverse direction, binary data back to PNG
* added `pyproject.toml` b/c `setup.py` and `pip install -e` *deprecation*
  - see [https://ichard26.github.io/blog/2024/08/whats-new-in-pip-24.2/](
         https://ichard26.github.io/blog/2024/08/whats-new-in-pip-24.2/)

These changes are very crude and not suitable for a pull request. They 
are primarily for learning and experimenting. Some (all?) of the
manipulations here could probably be done using Imagemagick to tweak
the PNG before even calling this program.

Example of running the program to generate Python output

`(.venv) $ rgb565-converter -b1 -i bb.png -o bb.py`

#### Python Image Class Definition:

This is the class generated by the Python output conversion.


```python
class Image:
  def __init__( self, _wid, _hgt, _packing, _buf):
    self.wid = _wid
    self.hgt = _hgt
    self.buf = _buf
    self.packing = _packing
```

The variable `packing` is an integer corresponding to the MicroPython 
framebuf type for either color RGB 565 or monochrome 4-bit grayscale 
as follows:

* `framebuf.RGB565 = 1`
* `framebuf.GS4_HMSB = 2`

#### Python Image Data:

```python
# image format: RGBA
icon = Image( 66, 72, 1,
  bytearray( [
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x62,
                            ... etc ...
    0x00,0x00,0x18,0xa0,0x51,0xe0,0x39,0x60,0x00,0x00,0x00,0x00,0x00,
    0x00,
  ] )
)
```

The name of the image is hard-coded to be `icon`, but can be easily
changed to be the file name (see code). It would be used like this in a
MicroPython program, possibly after compiling with `mpy-cross`:

```python
from someimage import icon

# create frame buffer
fb_icon = framebuf.FrameBuffer( icon.buf, 
          icon.wid, icon.hgt, icon.packing )

# blit to the screen
tft.blit_buffer( fb_icon, xpos, ypos, icon.wid, icon.hgt)

```



