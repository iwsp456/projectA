from django.contrib import admin
from .models import NerData, MrcData, InstaData, LstmData

# Register your models here.

admin.site.register(InstaData)
admin.site.register(NerData)
admin.site.register(MrcData)
admin.site.register(LstmData)