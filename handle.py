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
            print "Handle Post webdata is ", webData   #��̨����־
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                if recMsg.Content == 'h' or recMsg.Content == 'help' or recMsg.Content == '����':
                    content = "ʵʱ��Ʊ��ѯ��ʽ��������-Ŀ�ĵ�,������,����,����,��ѯ���Դ���\n�磺-f ���� -t ����ɽ -d 2016-09-30 -m z133 -n ����,Ӳ�� -r 3"
                else:
                    command = "php 12306.php " + recMsg.Content
                    content = subprocess.call([command])
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return replyMsg.send()
            else:
                print "���Ҳ�����"
                return "success"
        except Exception, Argment:
            return Argment