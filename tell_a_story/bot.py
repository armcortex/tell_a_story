import yaml
import json
import requests
import time


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

    def get_msg_id(self, msg, idx=0) -> str:
        res = self._get(5)
        ds = json.loads(res.text)
        for i, d in enumerate(ds):
            # print(f'{i=}: {d=}')
            if msg in d['content']:
                self.buf.append(d)

        return self.buf[idx]['id']


if __name__ == '__main__':
    b = PhotoBot('config.yaml')

    prompt = 'cute, robot, future, icon, air force, soldier'
    res = b.gen_photo(prompt)
    time.sleep(60)              # official announce that each photo gen need 60 seconds
    print(f'{res=}')

    msg_id = b.get_msg_id(prompt)
    print(f'{msg_id=}')

    res = b.upscale(0)
    print(f'{res=}')


