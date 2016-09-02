# -*- coding: utf-8 -*-
# filename: handle.py
import hashlib
import reply
import receive
import web
import os
import re
import sys 
#from subprocess import call
reload(sys)  
sys.setdefaultencoding("utf8")


class Handle(object):
    def POST(self):
        try:
            webData = web.data()
            print "Handle Post webdata is ", webData   #后台打日志
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName

                fromMsg=recMsg.Content.replace("|"," ")
                fromMsg=fromMsg.replace("  "," ")
                cmdFmtRegex = ur'\S+-\S+\s(\d{4}-\d{2}-\d{2})\s\S+\s\S'
                #if recMsg.Content == 'h' or recMsg.Content == 'help' or recMsg.Content == '帮助':
                if not re.match(cmdFmtRegex, fromMsg):
                    content = "实时余票查询格式：\n出发地-目的地 出发日 车次1,车次2 车座类型1,车位类型2\n例如：\n苏州-武汉 2016-09-30 d3022,d3066 二等座"
                else:
                    #command = "php /home/application/12306/12306/12306.php " + recMsg.Content
                    #cmdDetails=re.split(ur" ",fromMsg)
                    cmdDetails=fromMsg.split(" ")
                    if cmdDetails and len(cmdDetails)>=4:
                        fromToStation = cmdDetails[0].split("-")
                        fromStation = fromToStation[0].decode('utf-8')
                        toStation = fromToStation[1].decode('utf-8')
                        date = cmdDetails[1]
                        checi = cmdDetails[2]
                        seatType = cmdDetails[3].decode('utf-8')
                        command = "".join(["php /home/application/12306/12306/12306.php -f ",fromStation," -t ",toStation," -d ",date," -m ",checi," -n ",seatType," -r 1"])
                        print "command:"+ command
                        content = os.popen(command).read()
                        print "result:", content
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return replyMsg.send()
            else:
                print "暂且不处理"
                return "success"
        except Exception, Argment:
            return Argment
