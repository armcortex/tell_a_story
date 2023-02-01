import glob
from PIL import Image, ImageDraw, ImageFont

from utils import logging


img_path = './download/3/*.png'


def edit_image(filename: str, words: str):
    logging.info('Start')

    # Open the image
    img = Image.open(filename)

    # Create a draw object
    draw = ImageDraw.Draw(img)

    # Choose a font and font size
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 50)

    # Add the text to the image
    draw.text((10, 10), words, font=font, fill=(255, 255, 255))

    # Save the image
    img.save(filename)


def edit_image_batch(img_path: str):
    logging.info('Start')

    for i, f in enumerate(glob.glob(img_path)):
        word = f.split('/')[-1]
        print(f'{i=}, {f=}')
        edit_image(f, word)


def main():
    edit_image_batch(img_path)
    pass


if __name__ == '__main__':
    main()