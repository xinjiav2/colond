import argparse
from pathlib import Path

from PIL import Image

delimiter = "#" 
# seperate the bitsd in output

def text_to_bits(text: str) -> str:
    """Convert text to a string of bits."""
    encoded = text + delimiter
    return "".join(format(ord(char), "08b") for char in encoded)


def bits_to_text(bits: str) -> str:
    """convert string back to bits"""
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i : i + 8]
        if len(byte) < 8:
            break
        byte_array.append(int(byte, 2))
    return byte_array.decode("utf-8", errors="ignore")


def encode(image_path: str, text_file: str, output_path: str) -> None:
    secret_text = Path(text_file).read_text(encoding="utf-8")
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


def decode(image_path: str, output_path: str | None = None) -> str:
    """read hidden text from a png"""
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    extracted_bits: list[str] = []
    delimiter_bits = "".join(f"{byte:08b}" for byte in delimiter.encode("utf-8"))
    delimiter_length = len(delimiter_bits)

    for r, g, b in pixels:
        for val in (r, g, b):
            extracted_bits.append(str(val & 1))
            if (
                len(extracted_bits) >= delimiter_length
                and "".join(extracted_bits[-delimiter_length:]) == delimiter_bits
            ):
                content_bits = "".join(extracted_bits[:-delimiter_length])
                content = bits_to_text(content_bits)

                if output_path:
                    Path(output_path).write_text(content, encoding="utf-8")
                    print(f"Hidden text extracted and saved to {output_path}")

                return content

    print("No hidden text found in the image.")
    return ""


# cli
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Steganography tool to hide/extract text from/in an image")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", description="Encode text from a file into an image")
    encode_parser.add_argument("image", help="Path to the input image")
    encode_parser.add_argument("text", help="Path to the text file to hide")
    encode_parser.add_argument("output", help="Path to the output encoded image")
    encode_parser.set_defaults(func=lambda args: encode(args.image, args.text, args.output))

    decode_parser = subparsers.add_parser("decode", description="Decode text from an image")
    decode_parser.add_argument("image", help="Path to the input image")
    decode_parser.add_argument("--output", "-o", help="Path to output decoded text", default=None)
    decode_parser.set_defaults(func=lambda args: decode(args.image, args.output))

    args = parser.parse_args()
    result = args.func(args)

    if args.command == "decode" and not args.output and result:
        print("Hidden text:", result)

