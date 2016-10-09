from __future__ import unicode_literals

import datetime
import json
import requests
import time

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from djwechat import settings
# Create your models here.


class BaseWeixinApp(models.Model):
    secret = models.CharField(max_length=50, verbose_name=_('Secret'))
    token = models.CharField(max_length=50, verbose_name=_('Token'))
    aes_key = models.CharField(max_length=50, verbose_name=_('AESEncodingKey'))
    access_token = models.CharField(
        max_length=512, verbose_name=_('AccessToken'), blank=True, null=True)
    expire_time = models.DateTimeField(
        verbose_name=_('Expire Time'), blank=True, null=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class WeixinMP(BaseWeixinApp):
    secret = models.CharField(max_length=50, verbose_name=_('AppSecret'))
    appid = models.CharField(
        max_length=50, verbose_name=_('AppID'), unique=True)
    name = models.CharField(max_length=50, verbose_name=_('AppName'))

    def __str__(self):
        return 'AppID:%s,Name:%s' % (self.appid, self.name)

    def save(self, *args, **kwargs):
        if self._state.adding:
            super(WeixinMP, self).save(*args, **kwargs)
            return None
        now = timezone.now()
        if self.expire_time and self.expire_time > now:
            super(WeixinMP, self).save(*args, **kwargs)
            return None
        url = 'https://api.weixin.qq.com/cgi-bin/token'
        params = dict(grant_type='client_credential',
                      appid=self.appid, secret=self.secret)
        resp = requests.get(url=url, params=params)
        respj = resp.json()
        access_token = respj.get('access_token')
        expires_in = respj.get('expires_in')
        if not access_token or not expires_in:
            raise ValueError("Get AccessToken Failed: %s" % resp.content)
        self.access_token = access_token
        self.expire_time = now + datetime.timedelta(seconds=expires_in)

        super(WeixinMP, self).save(*args, **kwargs)

    class Meta:
        db_table = 'wechat_mp_server'
        verbose_name = _('WechatMP')
        verbose_name_plural = _('WechatMPs')


@python_2_unicode_compatible
class WeixinCorp(BaseWeixinApp):
    corpid = models.CharField(max_length=50, verbose_name=_('CorpID'))
    name = models.CharField(max_length=50, verbose_name=_('CorpName'))
    agentid = models.SmallIntegerField(verbose_name=_('AgentID'))
    agent_name = models.CharField(max_length=50, verbose_name=_('AgentName'))

    def __str__(self):
        return 'CorpID:%s,Name:%s' % (self.corpid, self.name)

    def save(self, *args, **kwargs):
        if self._state.adding:
            super(WeixinCorp, self).save(*args, **kwargs)
            return None
        now = timezone.now()
        if self.expire_time and self.expire_time > now:
            super(WeixinCorp, self).save(*args, **kwargs)
            return None
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        params = dict(corpid=self.corpid, corpsecret=self.secret)
        resp = requests.get(url=url, params=params)
        respj = resp.json()
        access_token = respj.get('access_token')
        expires_in = respj.get('expires_in')
        if not access_token or not expires_in:
            raise ValueError("Get AccessToken Failed: %s" % resp.content)
        self.access_token = access_token
        self.expire_time = now + datetime.timedelta(seconds=expires_in)

        super(WeixinCorp, self).save(*args, **kwargs)

    class Meta:
        db_table = 'wechat_corp_server'
        unique_together = ("corpid", "secret", "agentid")
        verbose_name = _('WechatCorp')
        verbose_name_plural = _('WechatCorps')


@python_2_unicode_compatible
class MPMenu(models.Model):
    app = models.ForeignKey(to=WeixinMP)
    menu = models.TextField(verbose_name=_('Menu'))

    def __str__(self):
        return 'Menu of AppName:%s' % self.app.name

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.app.access_token or not self.app.expire_time:
            raise ValueError("AccessToken is invalid")
        elif self.app.expire_time and self.app.expire_time < now:
            raise ValueError('AccessToken Expired')

        menu_create_url = 'https://api.weixin.qq.com/cgi-bin/menu/create'
        menu_get_url = 'https://api.weixin.qq.com/cgi-bin/menu/get'
        menu_delete_url = 'https://api.weixin.qq.com/cgi-bin/menu/delete'
        del_menu_resp = requests.get(url=menu_delete_url,
                                     params=dict(access_token=self.app.access_token))
        del_menu_respj = del_menu_resp.json()
        if not (0 == del_menu_respj.get('errcode') and 'ok' == del_menu_respj.get('errmsg').lower()):
            raise ValueError(del_menu_resp.content)
        # raise ValueError(self.menu)
        new_menu_resp = requests.post(url=menu_create_url,
                                      params=dict(
                                          access_token=self.app.access_token),
                                      data=json.dumps(json.loads(
                                          self.menu), ensure_ascii=False).encode('UTF-8'),
                                      headers={"Content-Type": "application/json; charset=UTF-8"})
        new_menu_respj = new_menu_resp.json()
        if not (0 == new_menu_respj.get('errcode') and 'ok' == new_menu_respj.get('errmsg').lower()):
            raise ValueError(new_menu_resp.content)

        super(MPMenu, self).save(*args, **kwargs)

    class Meta:
        db_table = 'wechat_mp_menu'
        verbose_name = _('MPMenu')
        verbose_name_plural = _('MpMenus')


@python_2_unicode_compatible
class CorpMenu(models.Model):
    corp = models.ForeignKey(to=WeixinCorp)
    menu = models.TextField(verbose_name=_('Menu'))

    def __str__(self):
        return 'Menu of AppName:%s,AgentName' % (self.corp.name, self.corp.agent_name)

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.corp.access_token or not self.corp.expire_time:
            raise ValueError("AccessToken is invalid")
        elif self.corp.expire_time and self.corp.expire_time < now:
            raise ValueError('AccessToken Expired')

        menu_create_url = 'https://qyapi.weixin.qq.com/cgi-bin/menu/create'
        menu_get_url = 'https://qyapi.weixin.qq.com/cgi-bin/menu/get'
        menu_delete_url = 'https://qyapi.weixin.qq.com/cgi-bin/menu/delete'
        del_menu_resp = requests.get(url=menu_delete_url,
                                     params=dict(access_token=self.corp.access_token,
                                                 agentid=self.corp.agentid))
        del_menu_respj = del_menu_resp.json()
        if not (0 == del_menu_respj.get('errcode') and 'ok' == del_menu_respj.get('errmsg').lower()):
            raise ValueError(del_menu_resp.content)
        new_menu_resp = requests.post(url=menu_create_url,
                                      params=dict(access_token=self.corp.access_token,
                                                  agentid=self.corp.agentid),
                                      data=json.dumps(json.loads(
                                          self.menu), ensure_ascii=False).encode('UTF-8'),
                                      headers={"Content-Type": "application/json; charset=UTF-8"})
        new_menu_respj = new_menu_resp.json()
        if not (0 == new_menu_respj.get('errcode') and 'ok' == new_menu_respj.get('errmsg').lower()):
            raise ValueError(new_menu_resp.content)

        super(CorpMenu, self).save(*args, **kwargs)

    class Meta:
        db_table = 'wechat_corp_menu'
        verbose_name = _('CorpMenu')
        verbose_name_plural = _('CorpMenus')
