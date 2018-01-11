from django.contrib import admin
from .models import TA, ChannelGroup, Channel,Channels_in_group,TA_in_channel


admin.site.register(TA)
admin.site.register(ChannelGroup)
admin.site.register(Channel)
admin.site.register(Channels_in_group)
admin.site.register(TA_in_channel)
