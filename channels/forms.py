from django import forms
from .models import ChannelGroup,Channels_in_group,Channel
from django.forms import ModelForm

class ChannelGroupForm(ModelForm):
    class Meta:
        model=ChannelGroup
        fields=['channelgroup_budget','channelgroup_R_fixed']
        widgets = {
            'channelgroup_budget': forms.TextInput(attrs={'class': 'pageelem','disabled':'disabled',"style":'width: 150px'}),
            'channelgroup_R_fixed': forms.TextInput(attrs={'class': 'pageelem',"style":'width: 150px'}),
        }

class Channels_in_groupForm(ModelForm):
    class Meta:
        model=Channels_in_group
        fields=['user_CPM','channel_budget_limit_min','channel_budget_limit_max','channel_fixed_budget','channel_fixed_show','channel_show_limit_max','channel_show_limit_min','channel_split_budget','channel_split_views',]
        widgets = {
            'channel_split_budget': forms.TextInput(attrs={"style":'width: 80px','disabled':'disabled'}),
            'channel_split_views': forms.TextInput(attrs={"style":'width: 80px','disabled':'disabled'}),
            'channel_budget_limit_min': forms.TextInput(attrs={"style": 'width: 140px'}),
            'channel_budget_limit_max': forms.TextInput(attrs={"style": 'width: 140px'}),
            'channel_show_limit_min': forms.TextInput(attrs={"style": 'width: 140px'}),
            'channel_show_limit_max': forms.TextInput(attrs={"style": 'width: 140px'}),
            'channel_fixed_budget': forms.TextInput(attrs={"style": 'width: 140px'}),
            'channel_fixed_show': forms.TextInput(attrs={"style": 'width: 140px'}),
            'user_CPM': forms.TextInput(attrs={"style": 'width: 120px'}),
        }

