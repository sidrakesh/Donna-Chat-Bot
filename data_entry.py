#!/usr/bin/python

import gflags
import leveldb
import re
import nltk
import json
import uuid
import sys
import os

db = leveldb.LevelDB('Knowledge_DB_data')

def main():

  files = [fi for fi in os.listdir('data') if os.path.isfile(os.path.join('data', fi))]

  for fi in files:
    with open(os.path.join('data', fi)) as f:
      data = json.load(f)
      json_str = json.dumps(data)
      db.Put(fi[:-5], json_str)

  print 'Data initialized'

if __name__ == '__main__':
  main()