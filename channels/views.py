from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, JsonResponse
from django.views.generic.edit import FormView
from django.views.generic.base import View

from .models import TA, ChannelGroup, Channels_in_group, Channel, TA_in_channel
from .forms import ChannelGroupForm, Channels_in_groupForm,TAForm,ChannelForm,TA_in_channelForm

from .tasks import task1, task2, task3, task4


# User registration modulte (up)

class RegisterFormView(FormView):
    form_class = UserCreationForm

    # Ссылка, на которую будет перенаправляться пользователь в случае успешной регистрации.
    # В данном случае указана ссылка на страницу входа для зарегистрированных пользователей.
    success_url = "/login/"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)

    # Опять же, спасибо django за готовую форму аутентификации.
    from django.contrib.auth.forms import AuthenticationForm

    # Функция для установки сессионного ключа.
    # По нему django будет определять, выполнил ли вход пользователь.
    from django.contrib.auth import login


class LoginFormView(FormView):
    form_class = AuthenticationForm

    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "login.html"

    # В случае успеха перенаправим на главную.
    success_url = "/"

    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()

        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


class LogoutView(View):
    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        logout(request)

        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect("/")


# User registration/authorization modulte (down)


# My func

def Administration(request):
    if request.user.is_superuser:

        if request.method=="GET":
            error = ""
            pass
        else:
            data = request.POST
            option=data['Option']
            error = []

            if option =="New_ta":
                form = TAForm(request.POST)
                if form.is_valid():
                   TAName = form.cleaned_data['TA_name']
                   TASize = form.cleaned_data['TA_Size']
                   New_TA = TA.objects.create(TA_name=TAName,TA_Size=TASize)
                   New_TA.save()
                else:
                    pass
            if option == "Delete_ta":
                TA_to_del = TA.objects.get(TA_id=data["TA_id"])
                Ta_in_channels_to_del=TA_in_channel.objects.filter(TA=TA_to_del)
                Ta_in_channels_to_del.delete()
                TA_to_del.delete()
            else:
                pass
            if option == "Change_ta":
                form = TAForm(request.POST)
                if form.is_valid():
                    TA_to_change=TA.objects.get(TA_id=data["TA_id"])
                    TA_to_change.TA_name = form.cleaned_data['TA_name']
                    TA_to_change.TA_Size = form.cleaned_data['TA_Size']
                    TA_to_change.save()
                else:
                    pass
            if option == "New_channel":
                form =ChannelForm(request.POST)
                if form.is_valid():
                    channel_name = form.cleaned_data["channel_name"]
                    New_channel=Channel.objects.create(channel_name=channel_name)
                    New_channel.save()
                else:
                    pass
            if option == "Delete_channel":
                channel_to_del = Channel.objects.get(channel_id=data["Сhannel_id"])
                Ta_in_channels_to_del=TA_in_channel.objects.filter(channel = channel_to_del)
                Ta_in_channels_to_del.delete()
                channel_to_del.delete()
            else:
                pass
            if option == "Change_channel":
                form = ChannelForm(request.POST)
                if form.is_valid():
                    Channel_to_change=Channel.objects.get(channel_id=data["channel_id"])
                    Channel_to_change.channel_name = form.cleaned_data['channel_name']
                    Channel_to_change.save()
                else:
                    pass
            if option == "New_settings":
                form = TA_in_channelForm(request.POST)
                if form.is_valid():
                    channel = form.cleaned_data["channel"]
                    ta = form.cleaned_data["TA"]
                    default_cpm=form.cleaned_data["default_CPM"]
                    TA_Z = form.cleaned_data["TA_CBU_Z"]
                    TA_P = form.cleaned_data["TA_CBU_P"]
                    TA_L = form.cleaned_data["TA_CBU_L"]
                    Channel_R = form.cleaned_data["Channel_TA_R"]

                    channel_test=TA_in_channel.objects.filter(channel=channel,TA=ta)
                    if (channel_test.__bool__() == False):
                        New_option = TA_in_channel.objects.create(channel=channel,TA=ta,default_CPM=default_cpm,TA_CBU_Z=TA_Z,TA_CBU_P=TA_P,TA_CBU_L=TA_L,Channel_TA_R=Channel_R)
                        New_option.save()
                    else:
                        error = "Данная целевая аудитория уже существует у данного канала."
                else:
                    pass
            if option == "Delete_settings_channel":
                list_to_del = TA_in_channel.objects.get(id=data["List_id"])
                list_to_del.delete()
            else:
                pass
            if option == "Change_channel_settings":
                form = TA_in_channelForm(request.POST)
                if form.is_valid():
                    channel = form.cleaned_data["channel"]
                    ta = form.cleaned_data["TA"]
                    default_cpm = form.cleaned_data["default_CPM"]
                    TA_Z = form.cleaned_data["TA_CBU_Z"]
                    TA_P = form.cleaned_data["TA_CBU_P"]
                    TA_L = form.cleaned_data["TA_CBU_L"]
                    Channel_R = form.cleaned_data["Channel_TA_R"]

                    if ((channel.channel_name!=data["old_Channel"])or(ta.TA_name!=data["old_TA"])):
                        test_list=TA_in_channel.objects.filter(TA=ta,channel=channel)
                        if (test_list.__bool__() == False):
                            list_to_del=TA_in_channel.objects.get(TA__TA_name=data["old_TA"],channel__channel_name=data["old_Channel"])
                            list_to_del.delete()
                            list_to_create=TA_in_channel.objects.create(TA=ta,channel=channel,default_CPM=default_cpm,TA_CBU_Z=TA_Z,TA_CBU_P=TA_P,TA_CBU_L=TA_L,Channel_TA_R= Channel_R)
                            list_to_create.save()
                        else:
                            error = "Эта связка уже существует."
                    else: # channels and TA not changed
                        list_to_update = TA_in_channel.objects.get(TA=ta,channel=channel)
                        list_to_update.default_CPM=default_cpm
                        list_to_update.TA_CBU_Z=TA_Z
                        list_to_update.TA_CBU_P=TA_P
                        list_to_update.TA_CBU_L=TA_L
                        list_to_update.Channel_TA_R=Channel_R
                        list_to_update.save()
                else:
                    pass

        return render(request, "Administration.html",
                      {'channels': Channel.objects.all(),"TA_in_channel":TA_in_channel.objects.all() ,"Channel_settings":TA_in_channelForm,'TAs': TA.objects.all(), 'Channel_Form':ChannelForm, 'TAForm': TAForm,"error":error})
    else:
        return HttpResponseNotFound("Access denied")


def deleteGroup(request):
    if request.method == 'GET':
        try:
            group_id = request.GET['Group_id']
            group = ChannelGroup.objects.get(channelgroup_id=group_id)
        except:
            return HttpResponseNotFound("<h1>Group not found</h1>")

        if group.channelgroup_Userowner != request.user:
            return HttpResponseNotFound("<h1>Page not found</h1>")
        channels_in_group = Channels_in_group.objects.filter(group_id=group_id)

        TA_id = group.channelgroup_TA.TA_id
        TA = group.channelgroup_TA

        included_channels = []
        channels_Tas_toshow = []

        channels_Tas = TA_in_channel.objects.filter(TA_id=TA_id)

        for channel in channels_in_group:
            channel = Channel.objects.get(channel_id=channel.channel_id)
            channel_name = channel.channel_name
            included_channels.append(channel)

            for ta in channels_Tas:
                if ta.channel_id == channel.channel_id:
                    channels_Tas_toshow.append(ta)

        return render(request, 'DeleteGroup.html',
                      {'group': group, 'channels': included_channels, 'Tas': channels_Tas_toshow})
    elif request.method == 'POST':
        post_data = request.POST
        group_id = post_data['groupid']
        group = ChannelGroup.objects.get(channelgroup_id=group_id)
        if group.channelgroup_Userowner != request.user:
            return HttpResponseNotFound("<h1>Page not found</h1>")
        channels_connections = Channels_in_group.objects.filter(group__channelgroup_id=group_id)
        channels_connections.delete()
        group.delete()
        return redirect('/My_groups')


def MainPage(request):
    return render(request, 'MainPage.html', {'user': request.user})


def all_channels(request):
    return render(request, 'Channels.html', {'channels': Channel.objects.all(), 'TA': TA.objects.all()})


def showgroups(request):
    if request.user.is_anonymous==True:
        return HttpResponseNotFound("<h1>Page not found</h1>")

    my_groups = ChannelGroup.objects.filter(channelgroup_Userowner=request.user)

    my_channels = []
    for group in my_groups:
        channels_in_group = Channels_in_group.objects.filter(group=group)
        my_channels.append([group.channelgroup_name, channels_in_group])

    for channel in my_channels:
        print(channel[0])
        print(channel[1])

    return render(request, 'My_groups.html', {'groups': my_groups, 'channels_in_groups': my_channels})


def showgroup(request):
    result = {}
    errors = []

    try:
        group_id = request.GET['Group_id']
    except:
        return HttpResponseNotFound("<h1>Page not found</h1>")

    try:
        group = ChannelGroup.objects.get(channelgroup_id=group_id)
    except:
        return HttpResponseNotFound("<h1>Page not found</h1>")

    if group.channelgroup_Userowner != request.user:
        return HttpResponseNotFound("<h1>Page not found</h1>")

    if request.method == 'POST':
        data = request.POST

        form = ChannelGroupForm(request.POST)

        if group.channelgroup_Userowner != request.user:
            return HttpResponseNotFound("<h1>Page not found</h1>")

        if form.is_valid():
            group.channelgroup_budget= form.cleaned_data['channelgroup_budget']
            group.channelgroup_R_fixed = form.cleaned_data['channelgroup_R_fixed']
            group.save()
        else:
            for error in form.errors:
                object=error
                object_error=form.errors[object][0] # i think this is not right method for this. Should be checked in first.
                errors.append(object + " - " + object_error)

        channels_in_group = Channels_in_group.objects.filter(group_id=group_id)  # список всех каналов / list with all channels

        for channel in channels_in_group:
            channel_id = channel.channel_id
            group_id = channel.group_id
            form = Channels_in_groupForm(request.POST,prefix=channel_id)
            if form.is_valid():
                channel.user_CPM=form.cleaned_data['user_CPM']
                channel.channel_budget_limit_max=form.cleaned_data['channel_budget_limit_max']
                channel.channel_budget_limit_min=form.cleaned_data['channel_budget_limit_min']
                channel.channel_fixed_budget=form.cleaned_data['channel_fixed_budget']
                channel.channel_fixed_show=form.cleaned_data['channel_fixed_show']
                channel.channel_show_limit_max=form.cleaned_data['channel_show_limit_max']
                channel.channel_show_limit_min=form.cleaned_data['channel_show_limit_min']
                channel.channel_split_budget=form.cleaned_data['channel_split_budget']
                channel.channel_split_views=form.cleaned_data['channel_split_views']
                channel.save()
            else:
                for error in form.errors:
                    object = error
                    object_error = form.errors[object][0]
                    errors.append(channel.channel.channel_name + " " + object + " - " + object_error)

        tasks = {'task1': task1, 'task2': task2, 'task3': task3, 'task4': task4}
        result = tasks[data['choice']](group_id=group_id)

    channels_in_group = Channels_in_group.objects.filter(
        group_id=group_id)  # список всех каналов / list with all channels

    TA_id = group.channelgroup_TA.TA_id

    Groupform = ChannelGroupForm(instance=group)

    #!!!
    channels_forms = []

    for channel in channels_in_group:
        channel_form = Channels_in_groupForm(instance=channel,prefix=channel.channel_id)
        channel_Ta=TA_in_channel.objects.get(channel__channel_id=channel.channel.channel_id,TA_id=TA_id)
        channels_forms.append([channel_form,channel_Ta,channel.channel.channel_name,channel.channel.channel_id])




    return render(request, 'Group.html',
                  {'group': group, 'result': result, 'groupform':Groupform, 'channels_forms':channels_forms,'errors':errors})

def return_TA(request):
    try:
        ta_id = request.GET['ta_id']
    except:
        return HttpResponseNotFound("<h1>Something went wrong. Please refresh the page</h1>")

    if request.is_ajax():
        TA_to_show=TA.objects.get(TA_id=ta_id)

        return JsonResponse({"TA_name":TA_to_show.TA_name,"TA_Size":TA_to_show.TA_Size,"TA_id":TA_to_show.TA_id})


def return_Channel(request):
    try:
        channel_id = request.GET['channel_id']
    except:
        return HttpResponseNotFound("<h1>Something went wrong. Please refresh the page</h1>")

    if request.is_ajax():
        Channel_to_show=Channel.objects.get(channel_id=channel_id)

        return JsonResponse({"channel_name":Channel_to_show.channel_name,"channel_id":Channel_to_show.channel_id})

def return_channels_onta(request):
    try:
        ta_id = request.GET['ta_id']
    except:
        return HttpResponseNotFound("<h1>Something went wrong. Please refresh the page</h1>")

    if ta_id == 0:
        message = "Channels not found"
        return HttpResponse(message)
    else:

        if request.is_ajax():
            Channel_list = TA_in_channel.objects.filter(TA_id=ta_id)

            html = ""
            channels = []
            for channel in Channel_list:
                channel = Channel.objects.get(channel_id=channel.channel_id)
                channel_name = channel.channel_name

                channel_robj = TA_in_channel.objects.get(channel_id=channel.channel_id, TA_id=ta_id)
                channel_r = channel_robj.Channel_TA_R

                channel_TA = TA.objects.get(TA_id=ta_id)
                channel_auditory = channel_TA.TA_Size * channel_r

                if request.user.is_authenticated:
                    html = html + "<br>" + channel_name + "<input class='checbox_data' style='position: relative;left: 60px' type='checkbox' name=chan" + str(
                        channel.channel_id) + "/>" + "<br> Охват в процентах: " + str(
                        channel_r) + "<br>Охват в людях: " + str(channel_auditory) +"<br>Цена за 1000 показов: "+ str(channel_robj.default_CPM)+"<br><br><br>"
                    channels.append({"channel_name":channel_name,"channel_id":str(channel.channel_id),"channel_r":str(channel_r),"channel_auditory":str(channel_auditory),"channel_cpm":str(channel_robj.default_CPM)})
                else:
                    html = html + "<br>" + channel_name + "<br> Охват в процентах: " + str(
                        channel_r) + "<br>Охват в людях: " + str(channel_auditory)+"<br>Цена за 1000 показов: "+ str(channel_robj.default_CPM) + "<br><br><br>"
                    channels.append({"channel_name": channel_name,
                                     "channel_id":channel.channel_id,
                                     "channel_r": str(channel_r), "channel_auditory": str(channel_auditory),
                                     "channel_cpm": str(channel_robj.default_CPM)})


        return JsonResponse({"channels":channels})

    return HttpResponse("Channels not found")

def return_ta_in_channels(request):
    try:
        id = request.GET['id']
    except:
        return HttpResponseNotFound("<h1>Something went wrong. Please refresh the page</h1>")

    if request.is_ajax():
        list_to_show=TA_in_channel.objects.get(id=id)
        return JsonResponse({"channel_name":list_to_show.channel.channel_name,"ta_name":list_to_show.TA.TA_name,"default_cpm":list_to_show.default_CPM,'TA_Z':list_to_show.TA_CBU_Z,'TA_P':list_to_show.TA_CBU_P,'TA_L':list_to_show.TA_CBU_L,"channel_r":list_to_show.Channel_TA_R,"id":list_to_show.id})


def showchannel_ingroup(request):
    try:
        group_id = request.GET['group_id']
        group = ChannelGroup.objects.get(channelgroup_id=group_id)
    except:
        return HttpResponseNotFound("<h1>Something went wrong. Please refresh the page.</h1>")

    if group.channelgroup_Userowner != request.user:
        return HttpResponseNotFound("<h1>Page not found</h1>")
    separator = " , "
    if group_id != 0:
        channels = Channel.objects.filter(channels_in_group__group__channelgroup_id=group_id)
        channels_names = []
        for channel in channels:
            channels_names.append(channel.channel_name)

        channels_names_string = separator.join(channels_names)

    return HttpResponse(channels_names_string)


def create_group(request):
    channel_list_id = []
    data = request.POST

    groupname = data['GroupName']

    TA_id = data['select_template']
    current_user = request.user

    for value in data:
        if value.startswith('chan'):
            channel_id = value[4:-1]
            channel_list_id.append(channel_id)

    Group = ChannelGroup.objects.create(channelgroup_name=groupname, channelgroup_Userowner=current_user,
                                        channelgroup_TA=TA.objects.get(TA_id=TA_id))
    new_group_id = Group.channelgroup_id
    Group.save()

    for channel_id in channel_list_id:
        new_channel = Channel.objects.get(channel_id=channel_id)
        new_group_channels = Channels_in_group.objects.create(group=Group, channel=new_channel)

    new_group_channels.save()

    return redirect('/showgroup/?Group_id=' + str(new_group_id))

# My func
