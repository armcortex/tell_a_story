import os
import copy
import time
import glob

from utils import logging, current_time, read_yaml, start_process, DOWNLOAD_BASE_PATH
from textbot import CHATGPT
from photobot import PhotoBot
from check_point import CheckPoint
from discordbot import write_msg_task

from edit_images import edit_image_batch
from gen_video import gen_video


def prompt_log(story_topic: str, time_str: str, styles: str, steps: str, steps_raw: str):
    file_path = f'./output/{time_str}_prompts_log.txt'
    with open(file_path, 'w+') as f:
        f.write(f'{"=" * 10} Story: {story_topic} Begin {"=" * 10}\n')

        f.write(f'{story_topic} \n\n')

        # All
        f.write('All: \n')
        f.write(f'{", ".join(styles)}, ')
        f.write(str(steps[0]))
        f.write('\n\n')

        # Styles
        f.write('Sytles: \n')
        f.write(', '.join(styles))
        f.write('\n\n')

        # Steps
        f.write('Steps:\n')
        for i, s in enumerate(steps):
            f.write(f'{i}. {str(s)}\n')
        f.write('\n\n')

        # Raw Steps
        f.write('Raw Steps: \n')
        f.write('\n'.join(steps_raw))

        f.write('\n\n')
        f.write(f'{"=" * 10} Story: {story_topic} End {"=" * 10}\n')


def print_star(msg: str):
    logging.info(f'{"*" * 10} {msg} {"*" * 10}')


def run_gen_story():
    write_msg_task(f'{"*" * 5} Start run_gen_story() {"*" * 5}')

    # if sys.platform == 'linux' or sys.platform == 'linux2':
    #     DOWNLOAD_BASE_PATH = './download/'
    # elif sys.platform == 'darwin':
    #     DOWNLOAD_BASE_PATH = '/Users/mcs51/code_storge/tell_a_story/download/'
    # else:
    #     raise ValueError('Only support linux and macOS')


    from time import perf_counter
    t1_start = perf_counter()


    # parameter settings
    story_filename = 'story_settings.yaml'
    story_cf = read_yaml(story_filename)

    bot_config_path = 'config.yaml'

    status_file_path = f'{DOWNLOAD_BASE_PATH}story_status.yaml'

    time_str = current_time()

    cp = CheckPoint(status_file_path)
    cp.check_init(time_str)
    time_str = cp.read_raw_data.folder_name

    for i_story_topic, story_topic in enumerate(story_cf['topics']):
        print_star(f'{i_story_topic+1}/{len(story_cf["topics"])} - Topic: {story_topic}')

        if cp.check_finished_topic(story_topic):
            print_star(f'Topic: {story_topic} Already finished')
            continue

        write_msg_task(f'Start {i_story_topic+1}/{len(story_cf["topics"])} - Topic: {story_topic}')

        if not cp.check_topic_exist(story_topic):
            story_style = f'please say English, and please list 10 style key word of {story_cf["story"]} story {story_topic}. Make sure all style word have diversity'
            story_steps = f'list {story_topic} full story step by step to the end with 10 steps, each step with only one sentence and with number count'

            # Generate Story guideline and style
            chatbot = CHATGPT(bot_config_path)
            try:
                styles, _ = chatbot.query(story_style, mode='keyword')
                steps, steps_raw = chatbot.query(story_steps, mode='sentence')
            except Exception as e:
                logging.error(f'{"=" * 20}  chatbot.query() error Begin {"=" * 20}')
                logging.error(f'Failed to query story: {story_topic}, error message: {e}')
                logging.error(f'Process restart')
                logging.error(f'{"=" * 20}  chatbot.query() error End {"=" * 20}')
                write_msg_task(f'{"*" * 5} chatbot.query() failed, restarting {"*" * 5}')

                start_process(run_gen_story)
                time.sleep(1)
                os.system(f'kill {os.getpid()}')

            steps_raw_copy = copy.deepcopy(steps_raw)
            cp.add_topic({'topic': story_topic, 'styles': styles, 'steps': steps, 'steps_raw': steps_raw_copy.split('\n\n')})
        else:
            styles, steps, steps_raw = cp.read_topic(story_topic)

        prompt_log(story_topic, time_str, styles, steps, steps_raw)

        # Generate Images
        img_cnt = 4
        photobot = PhotoBot(bot_config_path)

        for i_step, step in enumerate(steps):
            print_star(f'{i_step+1}/{len(steps)} of {i_story_topic+1}/{len(story_cf["topics"])} - Step: {step}')

            # Already finished last time
            if i_step < cp.check_step(story_topic):
                print_star(f'{i_step+1}/{len(steps)} {story_topic} - Already finished')
                continue

            write_msg_task(f'Start Steps: {i_step+1}/{len(steps)} {story_topic}')

            prompts = step + ', ' + ', '.join(styles)

            try:
                photobot.gen_photo(prompts)
            except Exception as e:
                logging.error(f'{"=" * 20}  gen_photo() error Begin {"=" * 20}')
                logging.error(f'Failed to generate photo in step {i_step=}, error message: {e}')
                logging.error(f'Process restart')
                logging.error(f'{"=" * 20}  gen_photo() error End {"=" * 20}')
                write_msg_task(f'{"*" * 5} gen_photo() failed, restarting {"*" * 5}')

                start_process(run_gen_story)
                # TODO: change sleep 20 minutes to cancel previous task function
                time.sleep(20*60)           # Make sure previous images is finish
                os.system(f'kill {os.getpid()}')

            try:
                photobot.upscale_multi(img_cnt)
            except Exception as e:
                logging.error(f'{"=" * 20}  upscale_multi() error Begin {"=" * 20}')
                logging.error(f'Failed to upscale photo in step {i_step=}, error message: {e}')
                logging.error(f'Process restart')
                logging.error(f'{"=" * 20}  upscale_multi() error End {"=" * 20}')
                write_msg_task(f'{"*" * 5} upscale_multi() failed, restarting {"*" * 5}')

                start_process(run_gen_story)
                # TODO: change sleep 20 minutes to cancel previous task function
                time.sleep(20*60)           # Make sure previous images is finish
                os.system(f'kill {os.getpid()}')


            # Create folder
            download_path = DOWNLOAD_BASE_PATH + f'{time_str}/{i_story_topic+1}_{story_topic}/org/'
            os.makedirs(download_path, exist_ok=True)

            # download images
            photobot.get_info(img_cnt)  # get last update message id
            for i_img in range(img_cnt):
                prefix_filename = f'{i_step+1}_{i_img+1}-{story_topic}'

                del_filename = download_path + prefix_filename
                for f in glob.glob(f'{del_filename}*.png'):
                    os.remove(f)

                try:
                    photobot.download_image(i_img, download_path=download_path, prefix=prefix_filename)
                except Exception as e:
                    logging.error(f'{"=" * 20}  download_image() error Begin {"=" * 20}')
                    logging.error(f'Failed to download image in {i_img=}, error message: {e}')
                    logging.error(f'Process restart')
                    logging.error(f'{"=" * 20}  download_image() error End {"=" * 20}')
                    write_msg_task(f'{"*"*5} download_image() failed, restarting {"*"*5}')

                    start_process(run_gen_story)
                    # time.sleep(1)
                    # TODO: change sleep 20 minutes to cancel previous task function
                    time.sleep(20 * 60)  # Make sure previous images is finish

                    os.system(f'kill {os.getpid()}')


            # Update progress
            cp.update_step_cnt(story_topic)

        cp.finish_topic(story_topic)

    cp.finish_all()


    t1_stop = perf_counter()
    diff = t1_stop - t1_start
    print(f'Execute Duration: {diff:.2f} sec, {diff/60:.2f} min')

    # fast mode: 20.4 mins
    # relax mode: 23.91 mins

    pass


    # # Generate Images
    # photobot = PhotoBot(photobot_filename)
    #
    # for i, step in enumerate(steps):
    #     prompts = step + ', ' + ', '.join(styles)
    #     _ = photobot.gen_photo(prompts)
    #     photobot.wait_event()
    #     _ = photobot.get_msg_id(prompts)
    #
    #     for idx in range(4):
    #         _ = photobot.upscale(idx)
    #         photobot.wait_event()
    #         _ = photobot.get_msg_id(prompts)
    #
    #         # Create folder
    #         folder_path = DOWNLOAD_BASE_PATH + time_str + '/org/'
    #         os.makedirs(folder_path, exist_ok=True)
    #
    #         # download images
    #         photobot.download_image(0, download_path=folder_path, prefix=f'{i+1}_{idx+1}-{story_topic}')
    #
    # # # Convert images for test
    # # # Create debug folder
    # # # folder_debug_path = DOWNLOAD_BASE_PATH + time_str + '/debug/'
    # #
    # # img_org_path = DOWNLOAD_BASE_PATH + 'test/org/'
    # #
    # # img_debug_path = DOWNLOAD_BASE_PATH + 'test/debug/'
    # # if not os.path.isdir(img_debug_path):
    # #     os.mkdir(img_debug_path)
    # #
    # # edit_img_path = img_org_path + '*.png'
    # # edit_image_batch(imgs_in=edit_img_path, imgs_out=img_debug_path)
    # #
    # # # Create Video
    # # edit_video_path = img_debug_path + '*.png'
    # # audio_path = './download/Body_On_Fire.mp3'
    # # output_video_path = img_debug_path + f'{time_str}_movie.mp4'
    # # gen_video(imgs_path=edit_video_path, audio_path=audio_path, output_path=output_video_path, img_duration=3.0)

