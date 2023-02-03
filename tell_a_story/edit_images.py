import glob
from PIL import Image, ImageDraw, ImageFont
from joblib import Parallel, delayed

from utils import logging


def edit_image(filename_in: str, filename_out: str, words: str):
    logging.info('Start')

    img = Image.open(filename_in)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 50)
    draw.text((10, 10), words, font=font, fill=(255, 255, 255))
    img.save(filename_out)


def edit_image_batch(imgs_in: str, imgs_out: str, format: str = '*.png'):
    def filename_convert():
        for i, f in enumerate(glob.glob(imgs_in + format)):
            word = f.split('/')[-1]
            out_path = imgs_out + word
            yield f, out_path, word

    logging.info('Start')

    Parallel(n_jobs=24, verbose=10)(
        delayed(edit_image)(*x) for x in filename_convert())


def main():
    from time import perf_counter

    base_path = './download/test/'
    in_path = base_path + 'org/'
    out_path = base_path + 'debug/'

    t1_start = perf_counter()

    edit_image_batch(imgs_in=in_path,
                     imgs_out=out_path)

    t1_stop = perf_counter()
    print(f'Execute Duration: {t1_stop - t1_start} sec')


if __name__ == '__main__':
    main()