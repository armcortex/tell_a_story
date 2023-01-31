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
        print('gen photo')
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
        print('upscale\n')

        # print(f'{self.buf=}')
        # print()
        msg_id = self.buf[idx]['id']
        msg_hash = self.buf[idx]['attachments'][0]['url'].split('_')[-1].split('.')[0]

        #             Globals.targetID = str(message.reference.message_id)
        # 	    #Get the hash from the url
        #             Globals.targetHash = str((message.reference.resolved.attachments[0].url.split("_")[-1]).split(".")[0])

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

        # 'custom_id': f'# MJ::JOB::upsample_max::{idx + 1}::{msg_hash}::SOLO'}}

                # 'custom_id': f'MJ::JOB::upsample::{idx}::c29730c4-e78e-4126-a732-82fa08780fad'}}

        print(f'upscale: {payload=}')

        # "guild_id": None,

        # {
        #     "type": 3,
        #     "nonce": "1070012720595599360",
        #     "guild_id": null,
        #     "channel_id": "1066324018120114187",
        #     "message_flags": 0,
        #     "message_id": "1070011034095599696",
        #     "application_id": "936929561302675456",
        #     "session_id": "c26781f653c612e23798e65262ea9ea5",
        #     "data": {
        #         "component_type": 2,
        #         "custom_id": "MJ::JOB::upsample::1::be8114e7-5e0a-47a1-89a9-f17ed6a15fd6"
        #     }
        # }

        return self._post(payload)

    def get_msg_id(self, msg, idx=0) -> str:
        print('get id')
        res = self._get(5)
        ds = json.loads(res.text)
        for i, d in enumerate(ds):
            print(f'{i=}: {d=}')
            if msg in d['content']:
                self.buf.append(d)
                # break

        return self.buf[idx]['id']
        pass


if __name__ == '__main__':
    b = PhotoBot('config.yaml')

    prompt = 'cute, robot, future, icon, air force, soldier'
    res = b.gen_photo(prompt)
    print(f'{res=}')

    time.sleep(60)
    b.get_msg_id(prompt)
    msg_id = b.upscale(0)
    print(f'{msg_id=}')

