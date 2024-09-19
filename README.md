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

These changes are very crude and not suitable for a pull request. They 
are primarily for learning and experimenting. Some (all?) of the
manipulations here could probably be done using Imagemagick to tweak
the PNG before even calling this program.

Example of running the program to generate Python output

```(.venv) $ rgb565-converter -b1 -i bb.png -o bb.py```


