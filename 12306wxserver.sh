#! /bin/bash

ps -ef | grep "python main.py 8081" | grep -v grep | cut -c 9-15 | xargs kill -s 9
nohup python main.py 8081 &1>/dev/null

