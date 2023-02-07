import os
import copy
# import yaml

import ruamel
from ruamel.yaml import YAML

# import dataclasses
# from dataclasses import dataclass
from pydantic import ValidationError, BaseModel
from pydantic.dataclasses import Field
from utils import logging, current_time, read_yaml, write_yaml, read_pickle, write_pickle


# TOPIC_CONTENT = {'topic': '',
#                  'styles': [],
#                  'steps': [],
#                  'steps_raw': [],
#                  'current_step': 0,
#                  'step_total_cnt': 0}


# class DataClassConfig(BaseModel):
#     validate_assignment = True


# @dataclass(config=DataClassConfig)
class TopicStatusData(BaseModel):
    done: bool = Field(default=False)

    class Config:
        validate_assignment = True


# @dataclass(config=DataClassConfig)
class TopicContentData(BaseModel):
    topic: str = Field(default='')
    step_total_cnt: int = Field(default=0)
    current_step: int = Field(default=0)
    styles: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)

    class Config:
        validate_assignment = True


# @dataclass(config=DataClassConfig)
class StoryData(BaseModel):
    folder_name: str = Field(default='')
    topics: list[str] = Field(default_factory=list)
    topics_status: list[TopicStatusData] = Field(default_factory=list)
    topics_content: list[TopicContentData] = Field(default_factory=list)


    # folder_name: str
    # topics: list[str]
    # topics_status: list[TopicStatusData]
    # topics_content: list[TopicContentData]

    class Config:
        validate_assignment = True



# ss = StoryData(folder_name='file_path', topics=['1', '2'], topics_status=[])
# print(ss)
#
# ss3 = StoryData(folder_name='file_path', topics=['1', '2'], topics_status=[TopicStatusData(done=False)])
# print(ss3)


# ss2 = StoryData(folder_name='file_path_2', topics=['1_2', '2_2'], topics_status=1)
# print(ss2)

# pass
# con = TopicContent(topic='Story_1', current_step=0, step_total_cnt=6, style=['s1_1', 's2_1', 's3_1'],
#               steps=['1_1', '2_1', '3_1'])





# class OrderedDumper(yaml.Dumper):
#     pass


class CheckPoint:
    def __init__(self, file_path: str):
        self.file_path = file_path

        self._d = StoryData()

        # self._d = StoryData(topics_status=[TopicStatusData()],
        #                     topics_content=[TopicContentData()])

        self.yaml = YAML()
        self.yaml.indent(mapping=4, sequence=4, offset=2)
        pass

    @staticmethod
    def _represent_dict_order(dumper, data):
        return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

    def _read(self):
        # tmp = read_yaml(self.file_path)

        # yaml.add_representer(dict, self._represent_dict_order)
        # with open(self.file_path, 'r') as f:
        #     # cf = yaml.safe_load(f)
        #     cf = yaml.load(f, Loader=yaml.SafeLoader)
        #
        # self._d = StoryData(**cf).dict()

        pass

    def _write(self):

        with open(self.file_path, 'w') as f:
            # yaml = ruamel.yaml.YAML()
            # self.yaml.default_flow_style = False
            # self.yaml.width = 256
            self.yaml.dump(self._d.dict(), f)


        # def load_yaml(file_path):
        #     with open(file_path, 'r') as file:
        #         data = ruamel.yaml.load(file, Loader=ruamel.yaml.RoundTripLoader)
        #     return data


        # write_yaml(self.file_path, self._d)

        # yaml.add_representer(dict, self._represent_dict_order)
        # with open(self.file_path, 'w') as f:
        #     yaml.dump(self._d.__dict__, f, Dumper=OrderedDumper)

        # with open(self.file_path, 'w') as f:
        #     self.yaml.dump(self._d.__dict__, f)
        pass

    def check_init(self, folder_name: str):
        self._d.folder_name = folder_name



        # if not os.path.exists(self.file_path):
        #     # self._d = {'folder_name': folder_name,
        #     #            'topics': [],                                    # Decide if run chatgpt
        #     #            'topics_status': [{'done': False}],
        #     #            'topics_content': [TOPIC_CONTENT]}
        #     # self._write()
        #
        #     # content_data = TopicContentData(topic='',
        #     #                                 current_step=0,
        #     #                                 step_total_cnt=0,
        #     #                                 style=[],
        #     #                                 steps=[''])
        #
        #     content_data = TopicContentData()
        #
        #     self._d = StoryData(folder_name=folder_name,
        #                         topics=[''],
        #                         topics_status=[TopicStatusData(done=False)],
        #                         topics_content=[content_data])
        #     self._write()
        # else:
        #     self._read()

    def add_topic(self, topic: dict):
        self._d.topics.append(topic['topic'])
        self._d.topics_status.append(TopicStatusData())
        content = TopicContentData(topic=topic['topic'],
                                   step_total_cnt=len(topic['steps']),
                                   styles=topic['styles'],
                                   steps=topic['steps'])
        self._d.topics_content.append(content)

        self._write()

        # status = TopicStatusData()


        # self._d['topics'].append(topic['topic'])
        #
        # content = copy.deepcopy(TOPIC_CONTENT)
        # content['topic'] = topic['topic']
        # content['styles'] = topic['styles']
        # content['steps'] = topic['steps']
        # content['step_total_cnt'] = len(topic['steps'])
        # self._d['topics_content'].append(content)
        # self._d['topics_content'].append(content)
        #
        # self._write()

    def check_topic_finish(self, topic: str) -> bool:
        idx = self._d['topics'].index(topic)
        if self._d['topics_status'][idx]['done']:
            return True
        else:
            return False

    def check_topic_content(self, topic: dict) -> bool:
        if topic['topic'] in self._d['topics']:
            return True
        else:
            self.add_topic(topic)
            return False

    def read_topic(self, topic: str):
        idx = self._d['topics'].index(topic)
        content = self._d['topics_content'][idx]
        if content['topic'] != topic:
            raise ValueError('Wrong Topic')

        return content['styles'], content['steps'], content['steps_raw']

    def finish_topic(self, topic:str):
        idx = self._d['topics'].index(topic)
        self._d['topics_status'][idx]['done'] = True
        self._write()

    def check_step(self, topic: str, idx: int) -> bool:
        idx = self._d['topics'].index(topic)
        content = self._d['topics_content'][idx]
        if content['current_step']+1 < content['step_total_cnt']:
            self.update_step_cnt(content, idx)
            return False
        else:
            return True

    def update_step_cnt(self, topic: str, cnt: int):
        idx = self._d['topics'].index(topic)
        self._d['topics_content'][idx]['step_total_cnt'] = cnt
        self._write()


if __name__ == '__main__':
    c = CheckPoint('./download/status_dataclass.yaml')
    c.check_init(current_time())

    t1 = {'topic': 'Story_1', 'styles': ['style_1_1', 'style_1_2', 'style_1_3'], 'steps': ['step_1_1', 'step_1_2', 'step_1_3']}
    t2 = {'topic': 'Story_2', 'styles': ['style_2_1', 'style_2_2', 'style_2_3'], 'steps': ['step_2_1', 'step_2_2', 'step_2_3']}
    c.add_topic(t1)
    c.add_topic(t2)

    pass






    # c = CheckPoint('./download/status.yaml')
    # c.check_init(current_time())
    #
    # t1 = {'topic': 'Story_1', 'styles': 'animation_1', 'steps': ['1_1', '2_1', '3_1']}
    # t2 = {'topic': 'Story_2', 'styles': 'animation_2', 'steps': ['1_2', '2_2', '3_2']}
    # t3 = {'topic': 'Story_3', 'styles': 'animation_3', 'steps': ['1_3', '2_3', '3_3']}
    # ts = [t1, t2, t3]
    #
    # c.add_topic(t1)

    # t1 = {'topic': 'Story_1', 'styles': ['s1_1', 's2_1', 's3_1'], 'steps': ['1_1', '2_1', '3_1']}
    #
    # # from dataclasses import dataclass
    # import yaml
    #
    # from pydantic import ValidationError
    # from pydantic.dataclasses import dataclass
    #
    #
    #
    #
    # @dataclass
    # class Data:
    #     topics: str
    #     styles: list
    #     steps: list
    #
    # # d = Data(topics='Story_1', styles=['s1_1', 's2_1', 's3_1'], steps=['1_1', '2_1', '3_1'])
    #
    # @dataclass
    # class test:
    #     a1: str
    #     a2: str
    #     a3: str
    #     a4: str
    #     a5: str
    #
    # t = test(a1='a1', a2='a2', a3='a3', a4='a4', a5='a5')
    #
    # t.a1 = 12
    #
    # class MyConfig:
    #     validate_assignment = True
    #
    # @dataclass(config=MyConfig)
    # class Content:
    #     topic: str
    #     current_step: int
    #     step_total_cnt: int
    #     style: list
    #     steps: list
    #
    # con = Content(topic='Story_1', current_step=0, step_total_cnt=6, style=['s1_1', 's2_1', 's3_1'], steps=['1_1', '2_1', '3_1'])

    # class OrderedDumper(yaml.Dumper):
    #     pass
    #
    #
    # def represent_dict_order(dumper, data):
    #     return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())
    #
    #
    # yaml.add_representer(dict, represent_dict_order)
    #
    # with open("./download/person.yaml", "w") as f:
    #     yaml.dump(con.__dict__, f, Dumper=OrderedDumper)


    # write_yaml('./download/dataclass_test.yaml', con.__dict__)

    pass



