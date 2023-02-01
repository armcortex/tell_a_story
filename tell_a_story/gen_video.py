import ffmpeg
import glob

from utils import logging, current_time


def gen_video(imgs_path: str, audio_path: str, output_path: str, img_duration: float, format: str = '*.png'):
    logging.info('Start')

    total_duration = len(glob.glob(imgs_path + format)) * img_duration
    video = ffmpeg.input(imgs_path + format, pattern_type='glob', framerate=float(1/img_duration))
    audio = ffmpeg.input(audio_path).filter('atrim', duration=total_duration)
    (
        ffmpeg.concat(video, audio, v=1, a=1)
        .output(output_path)
        .run()
    )


if __name__ == '__main__':
    base_path = './download/test/'
    imgs_path = base_path + 'debug/'
    audio_path = './download/Body_On_Fire.mp3'
    output_path = base_path + f'{current_time()}_movie.mp4'

    gen_video(imgs_path, audio_path, output_path, 3.0)
