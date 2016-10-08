from django.contrib import admin
from models import CorpMenu
from models import MPMenu
from models import WeixinCorp
from models import WeixinMP

# Register your models here.

admin.site.register(WeixinMP)
admin.site.register(WeixinCorp)
admin.site.register(MPMenu)
admin.site.register(CorpMenu)
