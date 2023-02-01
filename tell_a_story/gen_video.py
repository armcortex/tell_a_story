import ffmpeg
import datetime
import glob

from utils import logging


now = datetime.datetime.now()
now = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]

base_path = './download/3/'
imgs_path = base_path + 'named_revised/*.png'
output_path = base_path + f'{now}_movie.mp4'
audio_path = base_path + 'Body_On_Fire.mp3'


def gen_video(imgs_path: str, audio_path: str, output_path: str, img_duration: float):
    logging.info('Start')

    total_duration = len(glob.glob(imgs_path)) * img_duration
    video = ffmpeg.input(imgs_path, pattern_type='glob', framerate=float(1/img_duration))
    audio = ffmpeg.input(audio_path).filter('atrim', duration=total_duration)
    (
        ffmpeg.concat(video, audio, v=1, a=1)
        .output(output_path)
        .run()
    )


if __name__ == '__main__':
    gen_video(imgs_path, audio_path, output_path, 3.0)
