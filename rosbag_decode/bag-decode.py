from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr
from datetime import datetime

path = "rosbag_decode/test-logs/rosbag2_2021_06_01-19_24_43"

def list_topics_test():
    with Reader(path) as reader:
        # topic and msgtype information is available on .topics dict
        for topic, msgtype in reader.topics.items():
            print(topic, msgtype)


def deser_msg_test():
    with Reader(path) as reader:
        for topic, msgtype, timestamp, rawdata in reader.messages(['/waverunner/sys/ctrl/scenario_sys_time']):
            msg = deserialize_cdr(rawdata, msgtype)
            #decode from nanosecond timestamp
            readable_timestamp = datetime.fromtimestamp(timestamp*1E-9)
            print(readable_timestamp)
            print(msg.data)


if __name__ == "__main__":
    #deser_msg_test()
    list_topics_test()

