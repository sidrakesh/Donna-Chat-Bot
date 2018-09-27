#!/usr/bin/python

import gflags
import leveldb
import re
import nltk
import json
import uuid
import sys

gen_db = leveldb.LevelDB('Knowledge_DB_common')
db = leveldb.LevelDB('Knowledge_DB_data')

def main():
  id = 'start_state'

  lines = [line.rstrip('\n') for line in open(sys.argv[1])]

  i = 0
  while i < len(lines):
    inp = lines[i]
    out = lines[i+1]
    que = lines[i+2]
    i = i+3

    inp = inp.lower()
    # out = out.lower()

    inp_words = re.split(r'[ ,.?;]', inp)
    out_words = re.split(r'[ ]', out)
    que_words = re.split(r'[ ?]', que)

    out_words[:] = [x for x in out_words if x != ""]
    que_words[:] = [x for x in que_words if x != ""]

    inp_words[:] = [x for x in inp_words if x != ""]
    inp_words[:] = [x for x in inp_words if x != "a"]
    inp_words[:] = [x for x in inp_words if x != "the"]
    inp_words[:] = [x for x in inp_words if x != "an"]
    inp_words[:] = [x for x in inp_words if x != "are"]

    id = 'start_state'

    try:
      json_str = gen_db.Get(id)
      data = json.loads(json_str)
    except:
      data = {}
      data["$count"] = 0
      json_str = json.dumps(data)
      gen_db.Put('start_state', json_str)
    

    for word in inp_words:
      try:
        corres_json = data[word]
        corres_json["count"] = corres_json["count"] + 1
      except KeyError, e:
        corres_json = {}
        corres_json["id"] = str(uuid.uuid4())
        corres_json["count"] = 1
        data[word] = corres_json

      data["$count"] = data["$count"] + 1
      json_str = json.dumps(data)
      gen_db.Put(id, json_str)

      id = corres_json["id"]

      try:
        json_str = gen_db.Get(id)
        data = json.loads(json_str)
      except KeyError, e:
        data = {}
        data["$count"] = 0
        json_str = json.dumps(data)
        gen_db.Put(id, json_str)

    output_end_id = id

    #Start adding output sequence
    try:
      id = data["$response"]  
    except KeyError, e:
      data["$response"] = str(uuid.uuid4())
      data["$ask"] = str(uuid.uuid4())
      json_str = json.dumps(data)
      gen_db.Put(output_end_id, json_str)
      id = data["$response"]

    try:
      json_str = gen_db.Get(id)
      data = json.loads(json_str)
    except KeyError, e:
      data = {}
      data["$count"] = 0
      json_str = json.dumps(data)
      gen_db.Put(id, json_str)

    for word in out_words:
      try:
        corres_json = data[word]
        corres_json["count"] = corres_json["count"] + 1
      except KeyError, e:
        corres_json = {}
        corres_json["id"] = str(uuid.uuid4())
        corres_json["count"] = 1
        data[word] = corres_json

      data["$count"] = data["$count"] + 1
      json_str = json.dumps(data)
      gen_db.Put(id, json_str)

      id = corres_json["id"]

      try:
        json_str = gen_db.Get(id)
        data = json.loads(json_str)
      except KeyError, e:
        data = {}
        data["$count"] = 0
        json_str = json.dumps(data)
        gen_db.Put(id, json_str)

    try:
      corres_json = data["$stop"]
      corres_json["count"] = corres_json["count"] + 1
    except:
      corres_json = {"id": -1, "count": 1}

    data["$count"] = data["$count"] + 1
    data["$stop"] = corres_json
    json_str = json.dumps(data)
    gen_db.Put(id, json_str)

    

    #Start adding asking sequence

    json_str = gen_db.Get(output_end_id)
    data = json.loads(json_str)

    id = data["$ask"]

    try:
      json_str = gen_db.Get(id)
      data = json.loads(json_str)
    except KeyError, e:
      data = {}
      data["$count"] = 0
      json_str = json.dumps(data)
      gen_db.Put(id, json_str)

    for word in que_words:
      try:
        corres_json = data[word]
        corres_json["count"] = corres_json["count"] + 1
      except KeyError, e:
        corres_json = {}
        corres_json["id"] = str(uuid.uuid4())
        corres_json["count"] = 1
        data[word] = corres_json

      data["$count"] = data["$count"] + 1
      json_str = json.dumps(data)
      gen_db.Put(id, json_str)

      id = corres_json["id"]

      try:
        json_str = gen_db.Get(id)
        data = json.loads(json_str)
      except KeyError, e:
        data = {}
        data["$count"] = 0
        json_str = json.dumps(data)
        gen_db.Put(id, json_str)

    try:
      corres_json = data["$stop"]
      corres_json["count"] = corres_json["count"] + 1
    except:
      corres_json = {"id": -1, "count": 1}

    data["$count"] = data["$count"] + 1
    data["$stop"] = corres_json
    json_str = json.dumps(data)
    gen_db.Put(id, json_str)

  print 'Question formats initialized'

if __name__ == '__main__':
  main()