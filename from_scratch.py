#!/usr/bin/python

import os
import shutil

def main():
  try:
    shutil.rmtree('Knowledge_DB_common')
    shutil.rmtree('Knowledge_DB_data')
  except OSError:
    pass

  os.system('python data_entry.py')
  os.system('python question_answer_learning_rules.py question_formats.txt')
  os.system('python rules_entry.py common.txt')
  os.system('python seed_greetings.py')

  os.system('clear')

if __name__ == '__main__':
  main()