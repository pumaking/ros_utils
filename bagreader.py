import os

import rosbag

from python_utils.timeseriesu import DataSet
from ros_utils.util import tonp

import joblib

cachedir = os.path.join(os.path.expanduser('~'), '.cache', 'bagreader')
memory = joblib.Memory(cachedir, verbose=0)

@memory.cache()
def load_bag(filename, include=None, exclude=None):
  print("Reading bag %s..." % filename)
  bag = rosbag.Bag(filename)
  tt = bag.get_type_and_topic_info()

  all_topics = set(tt.topics.keys())

  if include is not None and exclude is not None:
    raise "Pass only one of include and exclude"
  elif include is not None:
    topics = [t for t in all_topics if any([it in t for it in include])]
  elif exclude is not None:
    topics = [t for t in all_topics if not any([it in t for it in exclude])]
  else:
    topics = all_topics

  data = DataSet()

  messages = bag.read_messages(topics)
  for topic, msg, msg_t in messages:
    datas = { 'meta_time' : msg_t.to_sec() }
    if hasattr(msg, 'header'):
      datas['time'] = msg.header.stamp.to_sec()
    else:
      datas['time'] = msg_t.to_sec()

    datas.update(**tonp(msg, excludes=['header']))

    data.add_point(topic, **datas)

  data.finalize()
  return data

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("bagfile", type=str)
  args = parser.parse_args()

  data = load_bag(args.bagfile)
  print(data)
