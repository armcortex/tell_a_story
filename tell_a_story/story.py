import os
import copy
import time

from utils import logging, current_time, read_yaml, write_yaml, read_pickle, write_pickle, start_process
from textbot import CHATGPT
from photobot import PhotoBot
from check_point import CheckPoint

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


# if __name__ == '__main__':

def run_gen_story():
    from time import perf_counter
    t1_start = perf_counter()


    # parameter settings
    story_filename = 'story_settings.yaml'
    story_cf = read_yaml(story_filename)

    bot_config_path = 'config.yaml'
    download_base_path = './download/'
    status_file_path = f'{download_base_path}story_status.yaml'

    time_str = current_time()

    cp = CheckPoint(status_file_path)
    cp.check_init(time_str)
    time_str = cp.read_raw_data.folder_name

    # parameter settings
    # story_topic = story_cf['topics'][25]
    # for story_topic in story_cf['topics'][:20]:


    for i_story_topic, story_topic in enumerate(story_cf['topics']):
        print_star(f'{i_story_topic+1}/{len(story_cf["topics"])} - Topic: {story_topic}')

        if cp.check_finished_topic(story_topic):
            print_star(f'Topic: {story_topic} Already finished')
            continue

        if not cp.check_topic_exist(story_topic):
            story_style = f'please say English, and please list 10 style key word of {story_cf["story"]} story {story_topic}. Make sure all style word have diversity'
            story_steps = f'list {story_topic} full story step by step to the end with 10 steps, each step with only one sentence and with number count'

            # Generate Story guideline and style
            chatbot = CHATGPT(bot_config_path)
            styles, _ = chatbot.query(story_style, mode='keyword')
            steps, steps_raw = chatbot.query(story_steps, mode='sentence')

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

            prompts = step + ', ' + ', '.join(styles)
            photobot.gen_photo(prompts)
            photobot.upscale_multi(img_cnt)

            # Create folder
            download_path = download_base_path + f'{time_str}/{i_story_topic+1}_{story_topic}/org/'
            os.makedirs(download_path, exist_ok=True)

            # download images
            photobot.get_info(img_cnt)  # get last update message id
            for i_img in range(img_cnt):
                # TODO: need to remove downloaded images, if previous step not work correctly

                try:
                    photobot.download_image(i_img, download_path=download_path, prefix=f'{i_step+1}_{i_img+1}-{story_topic}')
                except Exception as e:
                    logging.error(f'{"=" * 20}  download_image() error Begin {"=" * 20}')
                    logging.error(f'Failed to download image in {i_img=}, error message: {e}')
                    logging.error(f'Process restart')
                    logging.error(f'{"=" * 20}  download_image() error End {"=" * 20}')
                    start_process(run_gen_story)
                    time.sleep(1)


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
    #         folder_path = download_base_path + time_str + '/org/'
    #         os.makedirs(folder_path, exist_ok=True)
    #
    #         # download images
    #         photobot.download_image(0, download_path=folder_path, prefix=f'{i+1}_{idx+1}-{story_topic}')
    #
    # # # Convert images for test
    # # # Create debug folder
    # # # folder_debug_path = download_base_path + time_str + '/debug/'
    # #
    # # img_org_path = download_base_path + 'test/org/'
    # #
    # # img_debug_path = download_base_path + 'test/debug/'
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

