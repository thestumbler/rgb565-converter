#!/usr/bin/python3
import argparse
import os
from PIL import Image
from enum import Enum

class Mode(Enum):
    PY = ".py"
    CPP = ".cpp"
    PNG = ".png"

def main():
    parser = argparse.ArgumentParser(
        description="Convert a file from one format to another."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        dest="input_file",
        help="Input file to be converted."
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        dest="output_file",
        help="Output file to be converted."
    )
    parser.add_argument(
        "-s",
        "--swap",
        dest="swap",
        help="Swap bytes for 16-bit words."
    )
    parser.add_argument(
        "-b",
        "--bytes",
        dest="bytes",
        help="Saves as bytes instead of 16-bit words."
    )
    args = parser.parse_args()

    input_basename = os.path.basename(args.input_file).rsplit('.', 1)

    mode = Mode.CPP if (input_basename[1] == 'png') else Mode.PNG

    if args.output_file is None:
        args.output_file = input_basename[0] + mode.value

    output_basename = os.path.basename(args.output_file).rsplit('.', 1)

    if len(output_basename) != 2:
        print("Error: Invalid arguments.")
        exit(1)

    if (input_basename[1] not in ['png', 'cpp']):
        print("Error: Input file must be a .png or .cpp file.")
        exit(1)

    if (output_basename[1] not in ['png', 'cpp', 'py']):
        print("Error: Output file must be a .png or .cpp file.")
        print(f"Output file: {output_basename}")
        exit(1)

    if (input_basename[1] == output_basename[1]):
        print("Error: Input and output file must be different.")
        exit(1)

    if (mode == Mode.PNG):
        convert_rgb565_to_png(args)
    else:
        convert_png_to_rgb565(args)

def convert_png_to_rgb565(args):
    output_basename = os.path.basename(args.output_file).rsplit('.', 1)
    # name = output_basename[0]
    name = 'icon'
    png = Image.open(args.input_file)
    width, height = png.size

    if   output_basename[1] == 'png': omode = Mode.PNG
    elif output_basename[1] == 'cpp': omode = Mode.CPP 
    elif output_basename[1] == 'py':  omode = Mode.PY 

    if   omode == Mode.PNG: print("Out mode: PNG")
    elif omode == Mode.CPP: print("Out mode: CPP")
    elif omode == Mode.PY:  print("Out mode: PY")

    max_line_width = min(width, 72)

    # iterate over the pixels
    image = png.getdata()
    color = png.mode
    # MicroPython pixel format constants from the framebuf class
    # framebuf.RGB565 = 1
    # framebuf.GS4_HMSB = 2
    # for RGBA, Hackaday Wrencher logo, 
    # has almost all zeros as RGB and 
    # all the information is in the A channel
    # convert it to amber color...
    amber =	(255.0/255.0, 192.0/255.0, 0)

    print(f'image format: {color}' )

    if 'RGB' in color: # this is color image
      packing = 1
      rgb8 = [0,0]
      pixels = []
      for i, pix in enumerate(image):
        if len(pix) == 4:
          pixel=[0,0,0]
          for k in range(3):
            pixel[k] = int( pix[3] * amber[k] )
        else:
          pixel = pix
        # print(i, pixel)
        r = (pixel[0] >> 3) & 0x1F
        g = (pixel[1] >> 2) & 0x3F
        b = (pixel[2] >> 3) & 0x1F
        rgb = r << 11 | g << 5 | b
        if args.swap:
          rgb = ((rgb & 0xFF) << 8) | ((rgb & 0xFF00) >> 8)
        rgb8[0] = (rgb & 0xff00) >> 8
        rgb8[1] = (rgb & 0xff)
        pixels.extend( rgb8 )

    elif 'L' in color: # this is grayscale image
      packing = 2
      # hist = png.histogram()
      # for i, num in enumerate(hist):
      #   if num: 
      #     print(i, num)
      # get max / min
      gs_max = 0
      gs_min = 256
      for i, pix in enumerate(image):
        if type(pix) is int:  pixel = pix
        else:                 pixel = pix[1]
        if pixel > gs_max: gs_max = pixel
        elif pixel < gs_min: gs_min = pixel
        #print(f'{i:8}{pixel:8}{gs_min:8}{gs_max:8}')
      print(f'min/max: {gs_min}  {gs_max}')
      pixels = []
      gs = [] # temporary holding buffer
      for i, pix in enumerate(image):
        # get the pixel value
        if type(pix) is int:  pixel = pix
        else:                 pixel = pix[1]
        # scale and store in temporary nibble buffer
        gs.append( int(pixel/17) )
        if len(gs) >= 2:
          # build combined nibble
          pixels.append( ((gs[0] & 0x0f)<<4) + (gs[1] & 0x0f) )
          # reset
          gs = [] 
      # wrap up straggling pixel(s)
      if len(gs) == 1:
        pixels.append( (gs[0] & 0x0f)<<4 )

    # now print it
    image_content = "  "
    nominal_line_width = 64
    icol = 0
    for pixel in pixels:
      hexbyte = f'0x{pixel:02x},' 
      icol += len(hexbyte)
      image_content += hexbyte
      if icol > nominal_line_width:
        image_content += '\n    ' 
        icol = 0

    # wrap up, remove trailing newline if necessary
    if image_content.endswith('\n    '):
      image_content = image_content[:-5]

    output_h_content = f"""
#pragma once

// 3rdparty lib includes
#include <icon.h>

namespace icons {{
extern const espgui::Icon<{width}, {height}> {name};
}} // namespace icons
    """.strip() + "\n"

    output_cpp_content = f"""
#include "{name}.h"

namespace icons {{
const espgui::Icon<{width}, {height}> {name}{{{{
    {image_content}
}}, "{name}"}};
}} // namespace icons
    """.strip() + "\n"

    output_python_class = f"""
class Image:
  def __init__( self, _wid, _hgt, _packing, _buf):
    self.wid = _wid
    self.hgt = _hgt
    self.buf = _buf
    self.packing = _packing
    """.strip() + "\n\n\n"

    output_python_content = f"""
# image format: {color}
{name} = Image( {width}, {height}, {packing},
  bytearray( [
  {image_content}
  ] )
)
    """.strip() + "\n"

    if omode == Mode.CPP:
      with open(args.output_file, 'w') as output_file:
          output_file.write(output_cpp_content)
      with open(args.output_file.replace('.cpp', '.h'), 'w') as output_file:
          output_file.write(output_h_content)

    if omode == Mode.PY:
      with open(args.output_file, 'w') as output_file:
          output_file.write(output_python_class)
          output_file.write(output_python_content)

def convert_rgb565_to_png(args):
    with open(args.input_file, 'r') as input_file:
        tmp = input_file.read()
        icon_size = tmp.split('espgui::Icon<')[1].split('>')[0].replace(', ', ',').split(',')
        tmp = tmp.split('{{')[1].split('}')[0].split('\n')
        input_content = ""
        for line in tmp:
            input_content += line.split('//')[0].strip()
        input_content = input_content[0:-1].replace(', ', ',').split(',')

        width = int(icon_size[0])
        height = int(icon_size[1])
        png = Image.new('RGB', (width, height))

        for i, word in enumerate(input_content):
            r = (int(word, 16) >> 11) & 0x1F
            g = (int(word, 16) >> 5) & 0x3F
            b = (int(word, 16)) & 0x1F
            png.putpixel((i % width, i // width), (r << 3, g << 2, b << 3))

        png.save(args.output_file)

if __name__ == '__main__':
    main()
