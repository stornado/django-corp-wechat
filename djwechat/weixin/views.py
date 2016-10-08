from django.shortcuts import render
from django.views import View
# Create your views here.


class WechatMpServer(View):
    '''微信订阅号/服务号'''

    def get(self, request, appid):
        pass

    def post(self, request, appid):
        pass


class WechatCorpServer(View):
    '''微信企业号'''

    def get(self, request, corpid, agentid):
        pass

    def post(self, request, corpid, agentid):
        pass
