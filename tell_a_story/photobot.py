import os
import yaml
import json
import requests
import time

from utils import logging, current_time


class PhotoBot:
    def __init__(self, filename: str):
        self.info = None

        with open(filename, 'r') as f:
            self.cf = yaml.load(f, Loader=yaml.CLoader)

        self.header = {
            'authorization': self.cf['discord']['midjourney_bot']['token']
        }

    @staticmethod
    def _check_bot_finish(msg: str) -> bool:
        if not (('start' in msg) or ('%' in msg) or ('paused' in msg)):
            return True
        return False

    def _post(self, payload: dict):
        return requests.post('https://discord.com/api/v9/interactions',
                             headers=self.header,
                             json=payload,
                             )

    def _get(self, msg_cnt: int):
        ch_id = self.cf['discord']['midjourney_bot']['ch_id']
        return requests.get(f'https://discord.com/api/v9/channels/{ch_id}/messages?limit={msg_cnt}',
                            headers=self.header)

    def get_around(self, around_id: str, msg_cnt: int = 1):
        ch_id = self.cf['discord']['midjourney_bot']['ch_id']
        return requests.get(f'https://discord.com/api/v9/channels/{ch_id}/messages?limit={msg_cnt}&around={around_id}',
                            headers=self.header)

    def get_info(self, cnt: int = 1) -> list:
        self.info = json.loads(self._get(cnt).text)
        return self.info.reverse()

    def _gen_photo_raw(self, prompt: str):
        logging.info('Start')

        payload = {
            'type': 2,
            'application_id': self.cf['discord']['midjourney_bot']['app_id'],
            'channel_id': self.cf['discord']['midjourney_bot']['ch_id'],
            'session_id': self.cf['discord']['midjourney_bot']['session_id'],
            'data': {
                'version': '994261739745050686',
                'id': '938956540159881230',
                'name': 'imagine',
                'type': 1,
                'options': [{'type': 3, 'name': 'prompt', 'value': prompt}],
                'application_command': {
                    'id': '938956540159881230',
                    'application_id': self.cf['discord']['midjourney_bot']['app_id'],
                    'version': '994261739745050686',
                    'default_permission': True,
                    'default_member_permissions': False,
                    'type': 1,
                    'nsfw': False,
                    'name': "imagine",
                    'description': "There are endless possibilities...",
                    'dm_permission': True,
                    'options': [{
                        'type': 3,
                        'name': 'prompt',
                        'description': 'The prompt to imagine',
                        'required': True}]},
                'attachments': []}}

        return self._post(payload)

    def _upscale_raw(self, msg_idx: int, img_idx: int):
        logging.info('Start')

        msg_id = self.info[msg_idx]['id']
        msg_hash = self.info[msg_idx]['attachments'][0]['url'].split('_')[-1].split('.')[0]

        payload = {
            'type': 3,
            'channel_id': self.cf['discord']['midjourney_bot']['ch_id'],
            'message_flags': 0,
            'message_id': msg_id,
            'application_id': self.cf['discord']['midjourney_bot']['app_id'],
            'session_id': self.cf['discord']['midjourney_bot']['session_id'],
            'data': {
                'component_type': 2,
                'custom_id': f'MJ::JOB::upsample::{img_idx + 1}::{msg_hash}'}}

        return self._post(payload)

    def gen_photo(self, prompt: str):
        logging.info('Start')

        _ = self._gen_photo_raw(prompt)
        self.wait_event()

    def upscale_multi(self, num):
        logging.info('Start')

        self.get_info(1)        # Get gen_photo() message id
        for i in range(num):
            _ = self._upscale_raw(msg_idx=0, img_idx=i)

        self.wait_event_multi(num)

    def get_msg_id(self, mgs_idx: int = 0) -> str:
        return self.info[mgs_idx]['id']

    def get_msg(self, mgs_idx: int = 0) -> str:
        return self.info[mgs_idx]['content']

    def download_image(self, mgs_idx: int, download_path: str, prefix: str = '', suffix: str = ''):
        logging.info('Start')

        url = self.info[mgs_idx]['attachments'][0]['proxy_url']
        img_name, ext_name = self.info[mgs_idx]['attachments'][0]['filename'].split('.')

        if prefix:
            prefix = prefix + '-'

        if suffix:
            suffix = '-' + suffix

        filename = download_path + prefix + img_name + suffix + '.' + ext_name

        img = requests.get(url).content
        with open(filename, 'wb') as f:
            f.write(img)

    def wait_event(self):
        logging.info('Start')

        time.sleep(5)
        while True:
            self.get_info(1)
            msg = self.get_msg()

            if self._check_bot_finish(msg):
                break

            time.sleep(1)
        time.sleep(1)

    def wait_event_multi(self, num: int):
        logging.info('Start')

        time.sleep(5)
        while True:
            self.get_info(num)
            check = [self._check_bot_finish(self.get_msg(i)) for i in range(num)]
            if all(check):
                break

            time.sleep(1)
        time.sleep(1)


if __name__ == '__main__':
    img_cnt = 4
    prompt = 'cute, robot, future, icon, air force, soldier'
    download_path = './download/'

    b = PhotoBot('config.yaml')
    b.gen_photo(prompt)
    b.upscale_multi(img_cnt)

    # Download images
    download_path = download_path + current_time() + '/'
    os.makedirs(download_path, exist_ok=True)
    b.get_info(4)       # get last update message id
    for i in range(img_cnt):
        b.download_image(i, download_path=download_path, prefix=f'{i + 1}_{img_cnt}')


