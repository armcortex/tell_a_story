import yaml
import json
import requests
import time

from utils import logging


class PhotoBot:
    def __init__(self, filename: str):
        self.buf = []

        with open(filename, 'r') as f:
            self.cf = yaml.load(f, Loader=yaml.CLoader)

        self.header = {
            'authorization': self.cf['discord']['midjourney_bot']['token']
        }

    def _post(self, payload: dict):
        return requests.post('https://discord.com/api/v9/interactions',
                             headers=self.header,
                             json=payload,
                             )

    def _get(self, msg_cnt: id):
        ch_id = self.cf['discord']['midjourney_bot']['ch_id']
        return requests.get(f'https://discord.com/api/v9/channels/{ch_id}/messages?limit={msg_cnt}',
                            headers=self.header)

    def gen_photo(self, prompt: str):
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

    def upscale(self, idx: int):
        logging.info('Start')

        msg_id = self.buf[idx]['id']
        msg_hash = self.buf[idx]['attachments'][0]['url'].split('_')[-1].split('.')[0]

        payload = {
            'type': 3,
            'channel_id': self.cf['discord']['midjourney_bot']['ch_id'],
            'message_flags': 0,
            'message_id': msg_id,
            'application_id': self.cf['discord']['midjourney_bot']['app_id'],
            'session_id': self.cf['discord']['midjourney_bot']['session_id'],
            'data': {
                'component_type': 2,
                'custom_id': f'MJ::JOB::upsample::{idx + 1}::{msg_hash}'}}

        return self._post(payload)

    def get_msg_id(self, msg: str, idx: int = 0) -> str:
        logging.info('Start')
        self.buf = []

        res = self._get(5)
        ds = json.loads(res.text)
        for i, d in enumerate(ds):
            if msg.strip() in d['content']:
                self.buf.append(d)

        return self.buf[idx]['id']

    def download_image(self, idx: int, download_path: str, prefix: str = '', suffix: str = ''):
        logging.info('Start')

        url = self.buf[idx]['attachments'][0]['proxy_url']
        img_name, ext_name = self.buf[idx]['attachments'][0]['filename'].split('.')

        if prefix:
            prefix = prefix + '-'

        if suffix:
            suffix = '-' + suffix

        filename = download_path + prefix + img_name + suffix + '.' + ext_name

        img = requests.get(url).content
        with open(filename, 'wb') as f:
            f.write(img)

    def wait_event(self):
        def get_packege():
            res = self._get(1)
            return json.loads(res.text)[0]

        logging.info('Start')
        time.sleep(5)
        while True:
            msg = get_packege()['content']
            if not (('start' in msg) or ('%' in msg) or ('paused' in msg)):
                break
            time.sleep(1)

        time.sleep(1)


if __name__ == '__main__':
    b = PhotoBot('config.yaml')

    prompt = 'cute, robot, future, icon, air force, soldier'
    res = b.gen_photo(prompt)
    print(f'{res=}')
    b.wait_event()

    msg_id = b.get_msg_id(prompt)
    print(f'{msg_id=}')

    res = b.upscale(0)
    print(f'{res=}')
    b.wait_event()

    msg_id = b.get_msg_id(prompt)
    print(f'{msg_id=}')
    b.download_image(0, download_path='./download/')




