import sys
import os
import cv2
import numpy as np
import tempfile
import random
import colorama # time to beautify!

colorama.init()

def png_to_rustam(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    height, width, _ = img.shape

    rustam_data = []

    for y in range(height):
        for x in range(width):
            if img.shape[2] == 3:
                b, g, r = img[y, x]
                a = 255 # transparent image support, take that jpg!
            else:
                b, g, r, a = img[y, x]
            hex_color = f"{r:02X}{g:02X}{b:02X}{a:02X}"
            rustam_data.append(hex_color)

    width_bytes = width.to_bytes(4, byteorder="little")
    height_bytes = height.to_bytes(4, byteorder="little")
    path_to_rustam = os.path.splitext(image_path)[0] + ".rustam"

    with open(path_to_rustam, "wb") as file:
        file.write(width_bytes)
        file.write(height_bytes)
        for hex_color in rustam_data:
            file.write(bytes.fromhex(hex_color))

def rustam_to_png(file_path):
    with open(file_path, "rb") as file:
        width = int.from_bytes(file.read(4), byteorder="little")
        height = int.from_bytes(file.read(4), byteorder="little")
        pixel_data = file.read()

    img = np.zeros((height, width, 4), dtype=np.uint8)

    for i in range(0, len(pixel_data), 4):
        r = pixel_data[i]
        g = pixel_data[i+1]
        b = pixel_data[i+2]
        a = pixel_data[i+3]
        row = (i // 4) // width
        col = (i // 4) % width
        img[row, col] = [b, g, r, a]

    cv2.imwrite(TEMP_RESULT_PATH, img)

    return width, height

# this took painstakingly long
help_menu = f"""{colorama.Fore.GREEN}RUSTAM

{colorama.Fore.YELLOW}USAGE:
    {colorama.Style.RESET_ALL}{os.path.basename(__file__)} [FILE]
    {colorama.Style.RESET_ALL}{os.path.basename(__file__)} [SUBCOMMAND]

{colorama.Fore.YELLOW}SUBCOMMANDS:
    {colorama.Fore.GREEN}convert    {colorama.Style.RESET_ALL}Convert a image file to a .rustam file.
    {colorama.Fore.GREEN}help       {colorama.Style.RESET_ALL}Shows a help menu."""

def main():
    args = sys.argv
    
    if len(args) == 1:
        print(help_menu)
        return
    
    file_path = args[1]

    if args[1] == "convert":
        if len(args) < 3:
            raise ValueError(f"{colorama.Fore.RED}error: {colorama.Style.RESET_ALL}Secondary argument ('path') not provided. Example: python script.py convert image.png")
        
        path = args[2]
        print("Converting..")
        png_to_rustam(path)
        print(f"Successfully converted '{os.path.basename(path)}' into .RUSTAM")
    elif args[1] == "help":
        print(help_menu)
        return
    else:
        width, height = rustam_to_png(file_path)
        print(f"{width} {height}")

        img = cv2.imread(TEMP_RESULT_PATH)
        cv2.imshow("Image Viewer", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        os.remove(TEMP_RESULT_PATH)

if __name__ == "__main__":
    temp_dir = tempfile.gettempdir()
    TEMP_RESULT_PATH = os.path.join(temp_dir, f"{''.join(random.choices('ACBDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890', k=5))}.png")
    
    main()