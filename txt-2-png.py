import argparse
from PIL import Image, ImageDraw, ImageFont

delimiter = "#" 
# seperate the bitsd in output

def text_to_bits(text: str) -> str:
    """Convert text to a string of bits."""
    encode = text + delimiter
    return ''.join(format(ord(char), '08b') for char in encode)

def bits_to_text(bits: str) -> str:
    """convert string back to bits"""
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        byte_array.append(int(byte, 2))
    return byte_array.decode('utf-8', errors='ignore')

def encode(image_path: str, text: str, output_path: str) -> None:
    with open(text, "r", encoding = "utf-8") as file:
        secret_text = file.read()

    bits = text_to_bits(secret_text)
    total_bits = len(bits)

    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    max_bits = len(pixels) * 3  # 3 because each pixel can do r g or b
    if total_bits > max_bits:
        raise ValueError("Text is too long to encode in the image.")

    bit_index = 0
    new_pixels = []

    for r, g, b in pixels:
        channels = [r, g, b]
        for i in range(3):
            if bit_index < total_bits:
                channels[i] = (channels[i] & ~1) | int(bits[bit_index])
                bit_index += 1
        new_pixels.append(tuple(channels))

    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(new_pixels)
    encoded_img.save(output_path, "PNG")
    print(f"Text encoded and saved to {output_path}")

def decode(image_path: str, text: str, output_path: str) -> None:
    """read hidden text from a .png"""
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    extracted_bits = []
    delimiter_bits = "".join(
        f"{byte:08b}" for byte in delimiter.encode("utf-8")
    )
    delimiter_lenght = len(delimiter_bits)

    for r, g, b in pixels:
        for val in (r, g, b):
            extracted_bits.append(str(val & 1))
            if (
                len(extracted_bits) >= delimiter_lenght
                and "".join(extracted_bits[-delimiter_lenght:]) == delimiter_bits
            ):
                content_bits = "".join(extracted_bits[:-delimiter_lenght])
                content = bits_to_text(content_bits)

                if output_path:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Hidden text extracted and saved to {output_path}")

                return content

    print("No hidden text found in the image.")
    return ""



# cli
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="setenography tool to hide/extract text from/in image")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enc = argparse.ArgumentParser(description="encode text from file to image")
    enc.add_argument("image", help="Path to the input image")
    enc.add_argument("text", help="path to text file to hide")
    enc.add_argument("output", help="path to output encoded image")

    dec = argparse.ArgumentParser(description="decode text from image")
    dec.add_argument("image", help="Path to the input image")
    dec.add_argument("text", help="path to text file to hide")
    dec.add_argument("--output", "-o", help="path to output decoded text", default=None)    

    args = parser.parse_args()

    if args.command == "encode":
        encode(args.image, args.text, args.output)

    elif args.command == "decode":
        result = decode(args.image, args.output)
        if not args.output and result:
            print("Hidden text:", result)

