from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class TA(models.Model):
    class Meta():
        db_table = "TA"

    TA_id = models.AutoField(primary_key=True)
    TA_name = models.CharField(max_length=100, unique=True)
    TA_Size = models.IntegerField(validators=[
            MinValueValidator(1)
        ])

    def __str__(self):
        return (self.TA_name )


class ChannelGroup(models.Model):
    class Meta():
        db_table = "ChannelGroups"

    channelgroup_id = models.AutoField(primary_key=True)
    channelgroup_name = models.CharField(max_length=150)
    channelgroup_budget = models.FloatField(null=True, blank=True,validators=[
            MinValueValidator(0)
        ])
    channelgroup_Userowner = models.ForeignKey(User)
    channelgroup_TA = models.ForeignKey(TA)
    channelgroup_R_fixed = models.FloatField(null=True, blank=True,validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ])

    def __str__(self):
        return self.channelgroup_name + " Owner: " + self.channelgroup_Userowner.get_full_name()


class Channel(models.Model):
    class Meta():
        db_table = "Channel"

    channel_id = models.AutoField(primary_key=True)
    channel_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.channel_name


class Channels_in_group(models.Model):
    class Meta():
        db_table = "Channels_in_groups"

    group = models.ForeignKey(ChannelGroup)
    channel = models.ForeignKey(Channel)
    user_CPM = models.FloatField(blank=True, null=True,validators=[
            MinValueValidator(0)
        ])
    channel_budget_limit_min = models.FloatField(blank=True, null=True,validators=[
            MinValueValidator(0),
        ])
    channel_budget_limit_max = models.FloatField(blank=True, null=True,validators=[
            MinValueValidator(0)
        ])
    channel_show_limit_min = models.IntegerField(blank=True, null=True,validators=[
            MinValueValidator(0)
        ])
    channel_show_limit_max = models.IntegerField(blank=True, null=True,validators=[
            MinValueValidator(0)
        ])
    channel_fixed_budget = models.FloatField(blank=True, null=True,validators=[
            MinValueValidator(0)
        ])  # split in budget
    channel_fixed_show = models.IntegerField(blank=True, null=True,validators=[
            MinValueValidator(1)
        ])  # split in show
    channel_split_views = models.FloatField(null=True, blank=True, validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ])
    channel_split_budget = models.FloatField(null=True, blank=True, validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ])

    def __str__(self):
        ta = self.group.channelgroup_TA
        return (
            self.group.channelgroup_name + " Channel:" + self.channel.channel_name + " TA: "+ta.TA_name)


class TA_in_channel(models.Model):
    class Meta():
        db_table = "TA_in_channels"

    TA = models.ForeignKey(TA)
    channel = models.ForeignKey(Channel)
    default_CPM = models.FloatField(validators=[
            MinValueValidator(0)
        ])
    TA_CBU_Z = models.FloatField()
    TA_CBU_P = models.FloatField()
    TA_CBU_L = models.FloatField()
    Channel_TA_R = models.FloatField(validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ])

    def __str__(self):
        return (self.channel.channel_name + " TA: " + self.TA.TA_name)
