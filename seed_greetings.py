#!/usr/bin/python

import gflags
import leveldb
import re
import json
import uuid
import logging
import os
from random import randint
from datetime import date
import urllib

gen_db = leveldb.LevelDB('Knowledge_DB_common')

def add_greetings(user_greetings):
  data = {'greeting':user_greetings, '$count':len(user_greetings)}

  json_str = json.dumps(data)
  gen_db.Put('comp_greeting', json_str)

def main():
  greetings = ['Hi', 'Hey there', 'Hey', 'Hi!', 'Hey!']

  user_greetings = []

  for greeting in greetings:
    user_greetings.append({
      'value': greeting,
      'count': 1
    })

  add_greetings(user_greetings)

  print 'Greetings seeded'


if __name__ == '__main__':
  main()