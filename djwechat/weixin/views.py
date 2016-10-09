# -*- coding: utf-8 -*-

from corp.WXBizMsgCrypt import WXBizMsgCrypt as CORP
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from django.views import View
from models import WeixinCorp
from models import WeixinMP
from mp.WXBizMsgCrypt import WXBizMsgCrypt as MP
# Create your views here.


class WechatMpServer(View):
    '''微信订阅号/服务号'''

    def get(self, request, appid):
        mp = get_object_or_404(WeixinMP, appid=appid)
        sToken = mp.token
        sEncodingAESKey = mp.aes_key
        sAppID = mp.appid
        sToken = "QDG6eK"
        sEncodingAESKey = "jWmYm7qr5nMoAUwZRjGtBxmz3KA1tkAj3ykkR6q2B2C"
        sAppID = "wx5823bf96d3bd56c7"
        wxcpt = MP(sToken, sEncodingAESKey, sAppID)

        sVerifySign = request.GET.get('signature')
        sVerifyTimeStamp = request.GET.get('timestamp')
        sVerifyNonce = request.GET.get('nonce')
        sVerifyEchoStr = request.GET.get('echostr')
        ret, sEchoStr = wxcpt.VerifyURL(
            sVerifySign, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)

        if(ret != 0):
            return HttpResponse("ERR: VerifyURL ret: %d" % ret)

        return HttpResponse(sEchoStr)

    def post(self, request, appid):
        mp = get_object_or_404(WeixinMP, appid=appid)
        sToken = mp.token
        sEncodingAESKey = mp.aes_key
        sAppID = mp.appid
        wxcpt = CORP(sToken, sEncodingAESKey, sAppID)

        sReqMsgSig = request.GET.get('msg_signature')
        sReqTimeStamp = request.GET.get('timestamp')
        sReqNonce = request.GET.get('nonce')
        sReqData = request.body
        sReqMsgEncodingType = request.GET.get('encrypt_type', 'raw').lower()
        if 'aes' == sReqMsgEncodingType:
            ret, sMsg = wxcpt.DecryptMsg(
                sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
            if(ret != 0):
                return HttpResponse("ERR: DecryptMsg ret: %d" % ret)
        elif 'raw' == sReqMsgEncodingType:
            sMsg = sReqData

        sRespData = sMsg
        ret, sEncryptMsg = wxcpt.EncryptMsg(
            sRespData, sReqNonce, sReqTimeStamp)
        if(ret != 0):
            return HttpResponse("ERR: EncryptMsg ret: %d" % ret)
        return HttpResponse(sEncryptMsg, content_type='text/xml; charset=UTF-8')


class WechatCorpServer(View):
    '''微信企业号'''

    def get(self, request, corpid, agentid):
        corp = get_list_or_404(WeixinCorp, corpid=corpid, agentid=agentid)[0]
        sToken = corp.token
        sEncodingAESKey = corp.aes_key
        sCorpID = corp.corpid
        wxcpt = CORP(sToken, sEncodingAESKey, sCorpID)

        sVerifyMsgSig = request.GET.get('msg_signature')
        sVerifyTimeStamp = request.GET.get('timestamp')
        sVerifyNonce = request.GET.get('nonce')
        sVerifyEchoStr = request.GET.get('echostr')
        ret, sEchoStr = wxcpt.VerifyURL(
            sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)

        if(ret != 0):
            return HttpResponse("ERR: VerifyURL ret: %d" % ret)

        return HttpResponse(sEchoStr)

    def post(self, request, corpid, agentid):
        corp = get_object_or_404(WeixinCorp, corpid=corpid, agentid=agentid)
        sToken = corp.token
        sEncodingAESKey = corp.aes_key
        sCorpID = corp.corpid
        wxcpt = CORP(sToken, sEncodingAESKey, sCorpID)

        sReqMsgSig = request.GET.get('msg_signature')
        sReqTimeStamp = request.GET.get('timestamp')
        sReqNonce = request.GET.get('nonce')
        sReqData = request.body
        ret, sMsg = wxcpt.DecryptMsg(
            sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
        if(ret != 0):
            return HttpResponse("ERR: DecryptMsg ret: %d" % ret)

        sRespData = sMsg
        ret, sEncryptMsg = wxcpt.EncryptMsg(
            sRespData, sReqNonce, sReqTimeStamp)
        if(ret != 0):
            return HttpResponse("ERR: EncryptMsg ret: %d" % ret)
        return HttpResponse(sEncryptMsg, content_type='text/xml; charset=UTF-8')
