# colond
The Weird Storage card for creseent

least significant bit (lsb) stenography tool to hide `.txt` file inside a PNG image

## setup
1. create a and activate a virtual envionrment:
```fish
python3 -m venv venv
source venv/bin/activate.fish
```
2. install dependnecies:
pip install pillow

## how to encode

#### option a: use the cli

run `txt-2-png.py` with base image, secrete text file, and output path: ` python3 txt-2-png.py <base_image.png> <secret_file.txt> <output_image.png>` <br/>
eg: `python3 txt-2-png.py <test.png> <test.txt> <hidden.png>`

#### option b: use python directly
```python
from PIL import Image
import importlib

txt_2_png = importlib.import_module("txt-2-png")
txt_2_png.encode("input.png", "test.txt", "hidden.png")
```

please note that the base image must be a valid png large enough to hold all text bits (each pixel holds 3 bits: 1 bit per R, G, B channel).