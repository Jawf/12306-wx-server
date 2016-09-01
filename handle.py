# -*- coding: utf-8 -*-
# filename: handle.py
import hashlib
import reply
import receive
import web
from subprocess import call

class Handle(object):
    def POST(self):
        try:
            webData = web.data()
            print "Handle Post webdata is ", webData   #后台打日志
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                if recMsg.Content == 'h' or recMsg.Content == 'help' or recMsg.Content == '帮助':
                    content = "实时余票查询格式：出发地-目的地,出发日,车次,车座,查询尝试次数\n如：-f 北京 -t 井冈山 -d 2016-09-30 -m z133 -n 软卧,硬卧 -r 3"
                else:
                    command = "php 12306.php " + recMsg.Content
                    content = subprocess.call([command])
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return replyMsg.send()
            else:
                print "暂且不处理"
                return "success"
        except Exception, Argment:
            return Argment