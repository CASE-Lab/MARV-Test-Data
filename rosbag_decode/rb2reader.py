# for rosbag decoding
from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr
from datetime import datetime

# for file path handling
from pathlib import Path

# pandas
import pandas as pd

# rosbag type system imports
from rosbags.typesys import get_types_from_idl, get_types_from_msg, register_types
from rosbags.serde.messages import get_msgdef
from rosbags.typesys.types import FIELDDEFS

def list_topics(rosbag_path):
    with Reader(rosbag_path) as reader:
        # topic and msgtype information is available on .topics dict
        for topic, msgtype in reader.topics.items():
            print(topic, msgtype)

def print_info(rosbag_path):
    with Reader(rosbag_path) as reader:
        print("Duration: \t",reader.duration * 1E-9, "s")
        print("Message count: \t",reader.message_count)
        print("Start time: \t", datetime.fromtimestamp(reader.start_time * 1E-9))

def load_msg_defenition(msg_dict):
    """
    Takes in dict with name: pathlib paths to ros2 message files
    Tip: Check FIELDDEFS variable to verify correct message import
    """
    for name, path in msg_dict.items():
        msg_text = path.read_text()
        # plain dictionary to hold message definitions
        add_types = {}

        # add definition from one msg file (msg name needs to be actual msg name in ros)
        # message name prefix is removed to fix nested messages with local reference
        add_types.update(get_types_from_msg(msg_text, name))

        # make types available to rosbags serializers/deserializers
        register_types(add_types)


def topic2df(rosbag_path, topic_name, key_ignore_list=[], prefix=None) -> pd.DataFrame:
    with Reader(rosbag_path) as reader:
        msg_keys = []
        msg_values_list = []
        once = True
        if(not bool(list(reader.messages([topic_name])))):
            print("Error: No messages on topic", topic_name)
            return None
        for topic, msgtype, timestamp, rawdata in reader.messages([topic_name]):
            msg = deserialize_cdr(rawdata, msgtype)
            msg_vars = vars(msg)

            # create list of message keys:
            if once:
                once = False
                msg_keys = list(msg_vars.keys())
                for ignore_key in key_ignore_list:
                    try:
                        msg_keys.remove(ignore_key)
                    except:
                        print("Key", ignore_key, "not in msg_keys")

            msg_values = []
            for msg_key in msg_keys:
                #check for nested message defenition (only single depth for now)
                if hasattr(msg_vars[msg_key], '__dict__'):
                    msg_values.append(msg_vars[msg_key].__dict__)
                else:
                    msg_values.append(msg_vars[msg_key])

            msg_values_list.append(msg_values + [timestamp])
        #add prefix
        if prefix:
            msg_keys = [prefix + key for key in msg_keys]
        else:
            msg_keys = [topic_name + '/' + key for key in msg_keys]

        #append timestamp key
        msg_keys.append('timestamp')

        df = pd.DataFrame(data=msg_values_list, columns=msg_keys)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        return df

