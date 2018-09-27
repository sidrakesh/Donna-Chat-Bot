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

url = 'http://words.bighugelabs.com/api/2/0303ff6682fd8fc2dc3d737807ba355c/'

gen_db = leveldb.LevelDB('Knowledge_DB_common')
db = leveldb.LevelDB('Knowledge_DB_data')
logging.basicConfig(filename='Donna.log',level=logging.DEBUG)

def calc_age(birthday):
  date_fields = birthday.split('/')
  today = date.today()

  d = int(date_fields[0])
  m = int(date_fields[1])
  y = int(date_fields[2])

  if (today.month > m) or (today.month == m and today.day >= d):
    return str(today.year - y)

  return str(today.year - y - 1)

def find_data(ops, search_keys):
  #print search_keys

  try:
    json_str = db.Get(search_keys[0])
  except:
    response = urllib.urlopen(url + search_keys[0] + '/json')

    try:
      syn_data = json.loads(response.read())
    except ValueError:
      return "unknown"

    for syn in syn_data['noun']['syn']:
      try:
        json_str = db.Get(syn)
        break
      except:
        pass

  try:
    data = json.loads(json_str)
  except:
    return "unknown"


  for key in search_keys[1:]:
    if key in data:
      data = data[key]
    else:
      response = urllib.urlopen(url + key + '/json')

      try:
        syn_data = json.loads(response.read())
      except:
        return "unknown"

      found = False

      for syn in syn_data['noun']['syn']:
        try:
          data = data[syn]
          found = True
          break
        except:
          pass

      if found == False:
        return "unknown"
  
  try:
    val = data['value']
  except KeyError, e:
    return "unknown"

  for op in ops:
    if op == 'age':
      val = calc_age(val)

  return val

def greet_user():
  json_str = gen_db.Get('comp_greeting')
  data = json.loads(json_str)

  response = ''

  while response == '':
    for greeting in data['greeting']:
      i = randint(1, data['$count'])
      if(i <= greeting['count']):
        response = greeting['value']
        break

  return [1, response]

def add_greeting(user_greeting):
  try:
    json_str = gen_db.Get('comp_greeting')
    data = json.loads(json_str)
  except KeyError:
    data = {'greeting':[], '$count':0}

  for greeting in data['greeting']:
    if greeting['value'].lower() == user_greeting.lower():
      greeting['count'] = greeting['count'] + 1
      data['$count'] = data['$count'] + 1
      json_str = json.dumps(data)
      gen_db.Put('comp_greeting', json_str)
      return

  data['greeting'].append({'value': user_greeting,'count': 1})
  data['$count'] = data['$count'] + 1

  json_str = json.dumps(data)
  gen_db.Put('comp_greeting', json_str)

def ask_user(query):
  print_output('I\'m still a beginner, could you tell me how to respond to what you wrote?')

  answer = take_input()

  learn_from_user(query, answer)
  write_to_training_set(query, answer)

  print_output('thanks!')
  return answer

def write_to_training_set(query, answer):
  with open("common.txt", "a") as myfile:
    myfile.write("\n" + query)
    myfile.write("\n" + answer)

def learn_from_user(inp, out):
  inp = inp.lower()

  inp_words = re.split(r'[ ,.?!;]', inp)

  out_words = re.split(r'[ ]', out)

  out_words[:] = [x for x in out_words if x != ""]

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

  try:
    id = data["$response"]  
  except KeyError, e:
    data["$response"] = str(uuid.uuid4())
    json_str = json.dumps(data)
    gen_db.Put(id, json_str)
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

def get_data_from_id(id):
  json_str = gen_db.Get(id)
  return json.loads(json_str)

def get_words_list(data):
  l = []

  try:
    for key in data:
      l = l + data[key]['syn']
  except:
    pass

  return l

def respond_to_user(inp):
  #split input
  inp_words = re.split(r'[ ,.?!;]', inp)#.lower())
  inp_words[:] = [x for x in inp_words if x.lower() != ""]
  inp_words[:] = [x for x in inp_words if x.lower() != "a"]
  inp_words[:] = [x for x in inp_words if x.lower() != "the"]
  inp_words[:] = [x for x in inp_words if x.lower() != "an"]
  inp_words[:] = [x for x in inp_words if x.lower() != "are"]

  #start
  data = get_data_from_id('start_state')

  curr_arg = '$1'

  mapped_data = {}

  add_words_to_curr_arg = False

  for word in inp_words:
    if word.lower() not in data:
      #variable
      if curr_arg in data:
        data = get_data_from_id(data[curr_arg]['id'])
        add_words_to_curr_arg = True

      #words being added to current variable
      if add_words_to_curr_arg:
        if curr_arg not in mapped_data:
          mapped_data[curr_arg] = word
        else:
          mapped_data[curr_arg] = mapped_data[curr_arg] + ' ' + word
        continue

      #synonyms
      found_word = False

      try:
        response = urllib.urlopen(url + word.lower() + '/json')
        syn_data = json.loads(response.read())

        words_list = get_words_list(syn_data)
        for syn in words_list:
          if syn in data:
            word = syn
            found_word = True
            break
      except ValueError:
        pass

      if found_word == False:
        return [3, ask_user(inp)]

    elif curr_arg in mapped_data: #new variable name
      curr_arg_no = int(curr_arg[1:])
      curr_arg_no = curr_arg_no + 1
      curr_arg = "$" + str(curr_arg_no)
      add_words_to_curr_arg = False

    data = get_data_from_id(data[word.lower()]['id'])

  #print mapped_data

  ask_id = ''
  response_id = ''

  try:
    try:
      ask_id = data['$ask']
      response_id = data['$response']
    except KeyError:
      pass
    data = get_data_from_id(data['$response'])
  except KeyError, e:
    return [3, ask_user(inp)]

  response = ''

  while '$stop' not in data:
   
    # print i, ' and ', data['$count']
    word_selected = False
    while word_selected == False:
      for key in data:
        i = randint(1, data['$count'])
        # print 'Key count ', data[key]['count']
        if key != '$count' and key != '$ask' and key != '$response' and data[key]['count'] >= i:
          word_selected = True
          if key in mapped_data:
            response = response + mapped_data[key] + ' '
          elif key[-1] == ']':
            split_key = re.split(r'[\]\[:]', key)
            split_key[:] = [x for x in split_key if x != ""]

            if '^' in split_key:
              midi = split_key.index('^')
              search_args = split_key[midi+1:]
              ops = split_key[:midi]
            else:
              search_args = split_key
              ops = []

            search_keys = []
            for key_part in search_args:
              if key_part in mapped_data:
                search_keys.append(mapped_data[key_part].lower())
              else:
                search_keys.append(key_part.lower())
            
            str_data = find_data(ops, search_keys)
            if str_data == "unknown":
              return ask_question(ask_id, mapped_data, inp, response_id)
            response = response + str_data + ' '
          else:
            response = response + key + ' '

          data = get_data_from_id(data[key]['id'])
          break

  return [1, response]

def ask_question(ask_id, mapped_data, inp, response_id):
  try:
    data = get_data_from_id(ask_id)
  except KeyError, e:
    return [3, ask_user(inp)]

  question = ''

  while '$stop' not in data:
   
    # print i, ' and ', data['$count']
    word_selected = False
    while word_selected == False:
      for key in data:
        i = randint(1, data['$count'])
        # print 'Key count ', data[key]['count']
        if key != '$count' and key != '$ask' and key != '$response' and data[key]['count'] >= i:
          word_selected = True
          if key in mapped_data:
            question = question + mapped_data[key] + ' '
          else:
            question = question + key + ' '

          data = get_data_from_id(data[key]['id'])
          break

  question = question[:-1] + '?'

  return [2, question, response_id]

def acquire_knowledge(answer, response_id):
  ans_words = re.split(r'[ ]', answer)
  ans_words[:] = [x for x in ans_words if x != ""]

  curr_arg = '$1'

  mapped_data = {}

  data = get_data_from_id(response_id)

  add_words_to_curr_arg = False
  add_words_to_data = False

  answer_data = ''

  data_words = []

  i = -1

  for word in ans_words:
    i = i+1
    if word.lower() not in data:
      if word.lower() == 'the':
        continue
      #variable
      if curr_arg in data:
        data = get_data_from_id(data[curr_arg]['id'])
        add_words_to_curr_arg = True

      #words being added to current variable
      if add_words_to_curr_arg:
        if curr_arg not in mapped_data:
          mapped_data[curr_arg] = word
        else:
          mapped_data[curr_arg] = mapped_data[curr_arg] + ' ' + word
        continue

      data_key = ''

      for key in data:
        if key[0] == '[':
          data_key = key
          break

      if data_key != '':
        data_words = re.split(r'[ :\[\]]', data_key)
        data_words[:] = [x for x in data_words if x != ""]
        answer_data = " ".join(ans_words[i:])
        break

    elif curr_arg in mapped_data: #new variable name
      curr_arg_no = int(curr_arg[1:])
      curr_arg_no = curr_arg_no + 1
      curr_arg = "$" + str(curr_arg_no)
      add_words_to_curr_arg = False

    data = get_data_from_id(data[word.lower()]['id'])

  try:
    json_str = db.Get(mapped_data[data_words[0]].lower())
    data = json.loads(json_str)
  except KeyError:
    data = {}

  # print answer_data
  # for key in mapped_data:
  #   print key, mapped_data[key]

  # print data_words

  write_data = data

  for data_word in data_words[1:-1]:
    try:
      key_word = mapped_data[data_word].lower()
    except KeyError:
      key_word = data_word.lower()

    try:
      data = data[key_word]
    except KeyError:
      data[key_word] = {}
      data = data[key_word]

  try:
    data[mapped_data[data_words[-1]].lower()] = {
      "value": str(answer_data)
    }
  except:
    data[data_words[-1].lower()] = {
      "value": str(answer_data)
    }

  json_str = json.dumps(write_data, indent=2)
  db.Put(mapped_data[data_words[0]].lower(), json_str)

  with open(os.path.join('data', mapped_data[data_words[0]].lower() + '.json'), 'w') as f:
    f.write(json_str)

def take_input():
  print '\n>>',
  return str(raw_input())

def print_output(output):
  print '\nDonna:', output

def main():
  try:
    #random choice of who will greet first
    #0 means computer greets first, 1 means user greets first
    i = randint(0,1)

    if i == 0:
      inp = greet_user()
      print_output(inp[1])
    else:
      user_greeting = take_input()
      add_greeting(user_greeting)
      inp = respond_to_user(user_greeting)
      if inp[0] != 3:
        print_output(inp[1])

    while 1:
      out = take_input()

      # if inp[0] == 1:
      #   learn_from_user(inp[1], out)

      inp = respond_to_user(out)

      #ask user
      if inp[0] != 3:
        print_output(inp[1])

      #data learning
      if inp[0] == 2:
        out = take_input()
        acquire_knowledge(out, inp[2])
        print_output('I will remember that')

  except KeyboardInterrupt:
    print ''
    print_output('Bye!')
    os.system('clear')

  # except Exception, e:
  #   print 'An internal error has occured'
  #   Logger.error(str(e))

if __name__ == '__main__':
  main()