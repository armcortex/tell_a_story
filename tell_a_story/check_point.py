import os

from ruamel.yaml import YAML
from pydantic import BaseModel
from pydantic.dataclasses import Field

from utils import current_time


class TopicStatusData(BaseModel):
    done: bool = Field(default=False)

    class Config:
        validate_assignment = True


class TopicContentData(BaseModel):
    topic: str = Field(default='')
    step_total_cnt: int = Field(default=0)
    current_step: int = Field(default=0)
    styles: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    steps_raw: list[str] = Field(default_factory=list)

    class Config:
        validate_assignment = True


class StoryData(BaseModel):
    folder_name: str = Field(default='')
    topics: list[str] = Field(default_factory=list)
    topics_status: list[TopicStatusData] = Field(default_factory=list)
    topics_content: list[TopicContentData] = Field(default_factory=list)

    class Config:
        validate_assignment = True


class CheckPoint:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._d = StoryData()
        self.yaml = YAML()
        self.yaml.indent(mapping=4, sequence=4, offset=2)

    def _read(self):
        with open(self.file_path, 'r') as f:
            yaml = self.yaml.load(f)

        self._d = StoryData(**yaml)

    def _write(self):
        with open(self.file_path, 'w') as f:
            self.yaml.dump(self._d.dict(), f)

    @property
    def read_raw_data(self):
        return self._d

    def check_init(self, folder_name: str):
        if not os.path.exists(self.file_path):
            self._d.folder_name = folder_name
            self._write()
        else:
            self._read()

    def add_topic(self, topic: dict):
        self._d.topics.append(topic['topic'])
        self._d.topics_status.append(TopicStatusData())
        content = TopicContentData(topic=topic['topic'],
                                   step_total_cnt=len(topic['steps']),
                                   styles=topic['styles'],
                                   steps=topic['steps'],
                                   steps_raw=topic['steps_raw'])
        self._d.topics_content.append(content)
        self._write()

    def check_topic_exist(self, topic: str) -> bool:
        return topic in self._d.topics

    def check_finished_topic(self, topic: str) -> bool:
        if not self.check_topic_exist(topic):
            return False

        idx = self._d.topics.index(topic)
        return self._d.topics_status[idx].done

    def read_topic(self, topic: str):
        if not self.check_topic_exist(topic):
            raise ValueError(f'Topic not exist')

        idx = self._d.topics.index(topic)
        content = self._d.topics_content[idx]
        if content.topic != topic:
            raise ValueError(f'Wrong topic: {content.topic=} vs {topic=}')

        return content.styles, content.steps, content.steps_raw

    def finish_topic(self, topic: str):
        if not self.check_topic_exist(topic):
            raise ValueError(f'Topic not exist')

        idx = self._d.topics.index(topic)
        current_step = self._d.topics_content[idx].current_step
        step_total_cnt = self._d.topics_content[idx].step_total_cnt
        if current_step != step_total_cnt:
            raise ValueError(f'There is something on current_step cnt: {current_step=} vs {step_total_cnt}')

        self._d.topics_status[idx].done = True
        self._write()

    def check_step(self, topic: str) -> int:
        if not self.check_topic_exist(topic):
            raise ValueError(f'Topic not exist')

        idx = self._d.topics.index(topic)
        content = self._d.topics_content[idx]
        return content.current_step

    def update_step_cnt(self, topic: str):
        if not self.check_topic_exist(topic):
            raise ValueError(f'Topic not exist')

        idx = self._d.topics.index(topic)
        self._d.topics_content[idx].current_step += 1
        self._write()

    def finish_all(self):
        status = [x.done for x in self._d.topics_status]
        if all(status):
            os.remove(self.file_path)
        else:
            raise ValueError(f'No all topic is finish, please check again')


if __name__ == '__main__':
    filename = '1_test_checkpoint.yaml'
    time_str = current_time()
    t1 = {'topic': 'Story_1',
          'styles': ['style_1_1', 'style_1_2', 'style_1_3'],
          'steps': ['step_1_1', 'step_1_2', 'step_1_3'],
          'steps_raw': ['steps_raw_1_1', 'steps_raw_1_2', 'steps_raw_1_3']}

    t2 = {'topic': 'Story_2',
          'styles': ['style_2_1', 'style_2_2', 'style_2_3'],
          'steps': ['step_2_1', 'step_2_2', 'step_2_3'],
          'steps_raw': ['steps_raw_2_1', 'steps_raw_2_2', 'steps_raw_2_3']}

    import traceback

    def run_test(fn):
        try:
            fn()
        except Exception as e:
            traceback.print_exc()
            os.remove(filename)


    def check_read_write():
        c1 = CheckPoint(filename)
        c1.check_init(time_str)
        c1.add_topic(t1)
        c1_raw = c1.read_raw_data

        c2 = CheckPoint(filename)
        c2.check_init(time_str)
        c2_raw = c2.read_raw_data

        assert c1_raw == c2_raw

        print(f'Pass check_read_write()')
        os.remove(filename)

    run_test(check_read_write)

    def check_add_topic():
        c1 = CheckPoint(filename)
        c1.check_init(time_str)
        c1.add_topic(t1)
        c1.add_topic(t2)

        raw = c1.read_raw_data
        assert raw.topics_content[0].topic      == t1['topic']
        assert raw.topics_content[0].styles     == t1['styles']
        assert raw.topics_content[0].steps      == t1['steps']
        assert raw.topics_content[0].steps_raw  == t1['steps_raw']

        assert raw.topics_content[1].topic      == t2['topic']
        assert raw.topics_content[1].styles     == t2['styles']
        assert raw.topics_content[1].steps      == t2['steps']
        assert raw.topics_content[1].steps_raw  == t2['steps_raw']

        print(f'Pass check_add_topic()')
        os.remove(filename)


    run_test(check_add_topic)


    def check_finished_topic():
        c1 = CheckPoint(filename)
        c1.check_init(time_str)
        c1.add_topic(t1)

        # Check init state
        assert c1.check_finished_topic(t1['topic']) == False

        # Check current_step protection
        try:
            c1.finish_topic(t1['topic'])
        except:
            pass
        assert c1.check_finished_topic(t1['topic']) == False

        # Check set correct step cnt
        c1.update_step_cnt(t1['topic'])
        c1.update_step_cnt(t1['topic'])
        c1.update_step_cnt(t1['topic'])
        c1.finish_topic(t1['topic'])
        assert c1.check_finished_topic(t1['topic']) == True

        print(f'Pass check_finished_topic()')
        os.remove(filename)


    run_test(check_finished_topic)

    def check_read_topic():
        c1 = CheckPoint(filename)
        c1.check_init(time_str)
        c1.add_topic(t1)
        c1.add_topic(t2)

        styles, steps, steps_raw = c1.read_topic(t1['topic'])
        assert styles == t1['styles']
        assert steps == t1['steps']
        assert steps_raw == t1['steps_raw']

        styles, steps, steps_raw = c1.read_topic(t2['topic'])
        assert styles == t2['styles']
        assert steps == t2['steps']
        assert steps_raw == t2['steps_raw']

        print(f'Pass check_read_topic()')
        os.remove(filename)

    run_test(check_read_topic)

    def check_step():
        c1 = CheckPoint(filename)
        c1.check_init(time_str)
        c1.add_topic(t1)

        assert c1.check_step(t1['topic']) == 0

        c1.update_step_cnt(t1['topic'])
        c1.update_step_cnt(t1['topic'])
        assert c1.check_step(t1['topic']) == 2

        print(f'Pass check_step()')
        os.remove(filename)

    run_test(check_step)




