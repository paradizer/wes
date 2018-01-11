from .models import TA, ChannelGroup, Channels_in_group, Channel, TA_in_channel

from django.shortcuts import render, redirect

from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django.views.generic.edit import FormView
from django.views.generic.base import View

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound,JsonResponse
from itertools import product

from django.core import serializers
from .forms import ChannelGroupForm,Channels_in_groupForm
from .tasks import task1, task2, task3, task4


STEP = 10


def count_r(views, ta):
    return views ** ta.TA_CBU_P / (views ** ta.TA_CBU_P + ta.TA_CBU_Z ** ta.TA_CBU_P) * ta.TA_CBU_L


def total_r(rs):
    result = 1
    for r in rs:
        result *= (1-r)
    return 1 - result


def get_split(data):
    return [round(i/sum(data), 2) for i in data] if sum(data) != 0 else [0]*len(data)

#
# def task1(group_id=1):
#     try:
#         channels_in_group_list = list(Channels_in_group.objects.filter(group_id=group_id)) #list of all channells for asked group
#         total_budget = channels_in_group_list[0].group.channelgroup_budget
#         ta = channels_in_group_list[0].group.channelgroup_TA
#         ta_in_channel_list = [TA_in_channel.objects.get(channel=i.channel, TA=ta) for i in channels_in_group_list]
#         chan_number = len(channels_in_group_list)
#         cp_list = [channel.user_CPM / 1000 if channel.user_CPM else ta_in_channel_list[i].default_CPM / 1000 for i, channel in enumerate(channels_in_group_list)]
#         views = []
#         for number, channel in enumerate(channels_in_group_list):
#             min_range = channel.channel_show_limit_min if channel.channel_show_limit_min else 0
#             min_range = round(channel.channel_budget_limit_min / cp_list[number]) if channel.channel_budget_limit_min else min_range
#             max_range = channel.channel_show_limit_max if channel.channel_show_limit_max else round((total_budget/cp_list[number]))
#             max_range = round(channel.channel_budget_limit_max / cp_list[number]) if channel.channel_budget_limit_max else max_range
#             views_for_channel = range(min_range, max_range + STEP, STEP)
#             if channel.channel_fixed_show:
#                 views_for_channel = [channel.channel_fixed_show]
#             if channel.channel_fixed_budget:
#                 views_for_channel = [round(channel.channel_fixed_budget/cp_list[number])]
#             views.append(views_for_channel)
#         rmax = 0
#         views_best = 0
#         budget = 0
#         for views_list in product(*views):
#             if sum(views_list[i] * cp_list[i] for i in range(chan_number)) > total_budget:
#                 continue
#             r_list = [count_r(views_list[i], ta_in_channel_list[i]) for i in range(chan_number)]
#             r = total_r(r_list)
#             if r > rmax:
#                 rmax = r
#                 budget = [views_list[i] * cp_list[i] for i in range(chan_number)]
#                 views_best = views_list
#         if budget == 0:
#             return {'error': "sorry, can't find answer with this params"}
#         r = rmax
#         return {'task': 1, 'r': r, 'budget_split': get_split(budget), 'budget': budget, 'views': views_best,
#                 'r_perc': round(r * 100, 1), 'r_people': round(r * ta.TA_Size / 1000, 3), 'views_split': get_split(views_best)}
#     except Exception as e:
#         return {'error': "Unexpected error: {}".format(e)}
#
#
# def task2(group_id=1):
#     try:
#         channels_in_group_list = list(Channels_in_group.objects.filter(group_id=group_id)) #list of all channells for asked group
#         total_budget = channels_in_group_list[0].group.channelgroup_budget
#         ta = channels_in_group_list[0].group.channelgroup_TA
#         ta_in_channel_list = [TA_in_channel.objects.get(channel=i.channel, TA=ta) for i in channels_in_group_list]
#         chan_number = len(channels_in_group_list)
#         cp_list = [channel.user_CPM / 1000 if channel.user_CPM else ta_in_channel_list[i].default_CPM / 1000 for i, channel in enumerate(channels_in_group_list)]
#         views_split = [channel.channel_split_views for channel in channels_in_group_list if channel.channel_split_views]
#         budget_split_by_views = []
#         if views_split:
#             if len(views_split) != chan_number or sum(views_split) != 1:
#                 return {'error': 'Check views split'}
#             #count budget split based on views split
#             budget_split_by_views = get_split([views_split_ch * cp_list_ch for views_split_ch, cp_list_ch in zip(views_split, cp_list)])
#
#         budget_split = budget_split_by_views or [channel.channel_split_budget for channel in channels_in_group_list if channel.channel_split_budget]
#         if budget_split:
#             if len(budget_split) != chan_number or round(sum(budget_split), 1) != 1:
#                 return {'error': 'Check budget split', 'budget_split': budget_split}
#             else:
#                 budget_list = [total_budget * ch_budget_p for ch_budget_p in budget_split]
#                 #check max channel budgets
#                 for number, channel in enumerate(channels_in_group_list):
#                     limit_max = channel.channel_budget_limit_max or channel.channel_show_limit_max * cp_list[number] if channel.channel_show_limit_max else None
#                     if limit_max:
#                         budget_list_var = [limit_max / budget_split[number] * ch_budget_p for ch_budget_p in budget_split]
#                         if sum(budget_list_var) < sum(budget_list):
#                             budget_list = budget_list_var
#                 #check for min budgets
#                 for number, channel in enumerate(channels_in_group_list):
#                     limit_min = channel.channel_budget_limit_min or channel.channel_show_limit_min*cp_list[number] if channel.channel_show_limit_min else None
#                     if limit_min and limit_min > budget_list[number]:
#                         return {'error': 'min budget for channel {} is more than possible budget split and max for other groups'.format(channel.channel.channel_name)}
#                 views_list = [round(ch_budget / cp_list[i]) for i, ch_budget in enumerate(budget_list)]
#                 r_list = [count_r(views_list[i], ta_in_channel_list[i]) for i in range(chan_number)]
#                 r = round(total_r(r_list), 3)
#                 return {'task': 2, 'r': r, 'budget_split': budget_split, 'budget': round(sum(budget_list)), 'views': views_list,
#                         'views_split': get_split(views_list), 'r_perc': round(r * 100, 1), 'r_people': round(r * ta.TA_Size / 1000, 3)}
#         return {'error': 'check splits'}
#     except Exception as e:
#         return {'error': "Unexpected error: {}".format(e)}
#
# def task3(group_id=1):
#     try:
#         channels_in_group_list = list(Channels_in_group.objects.filter(group_id=group_id)) #list of all channells for asked group
#         total_budget = 5000
#         ta = channels_in_group_list[0].group.channelgroup_TA
#         ta_in_channel_list = [TA_in_channel.objects.get(channel=i.channel, TA=ta) for i in channels_in_group_list]
#         chan_number = len(channels_in_group_list)
#         cp_list = [channel.user_CPM / 1000 if channel.user_CPM else ta_in_channel_list[i].default_CPM / 1000 for i, channel in enumerate(channels_in_group_list)]
#         views = []
#         for number, channel in enumerate(channels_in_group_list):
#             min_range = channel.channel_show_limit_min if channel.channel_show_limit_min else 0
#             min_range = round(channel.channel_budget_limit_min / cp_list[number]) if channel.channel_budget_limit_min else min_range
#             max_range = channel.channel_show_limit_max if channel.channel_show_limit_max else round((total_budget/cp_list[number]))
#             max_range = round(channel.channel_budget_limit_max / cp_list[number]) if channel.channel_budget_limit_max else max_range
#             views_for_channel = range(min_range, max_range + STEP, STEP)
#             if channel.channel_fixed_show:
#                 views_for_channel = [channel.channel_fixed_show]
#             if channel.channel_fixed_budget:
#                 views_for_channel = [round(channel.channel_fixed_budget/cp_list[number])]
#             views.append(views_for_channel)
#         r_fixed = channels_in_group_list[0].group.channelgroup_R_fixed
#         min_budget = 10**10
#         views_best = 0
#         budget = 0
#         used_r = 0
#         for views_split in product(*views):
#             current_budget = sum(views_split[i] * cp_list[i] for i in range(chan_number))
#             if current_budget > min_budget:
#                 continue
#             r_list = [count_r(views_split[i], ta_in_channel_list[i]) for i in range(chan_number)]
#             r = total_r(r_list)
#             if r >= r_fixed:
#                 used_r = r
#                 min_budget = current_budget
#                 budget = [views_split[i] * cp_list[i] for i in range(chan_number)]
#                 views_best = views_split
#         if budget == 0:
#             return {'error': "sorry, can't find answer with this params"}
#         r = used_r
#         return {'task': 3, 'min_budget': min_budget, 'r': r, 'budget_split': get_split(budget), 'budget': sum(budget),
#                 'views': views_best, 'views_split': get_split(views_best), 'r_perc': round(r * 100, 1), 'r_people': round(r * ta.TA_Size / 1000, 3)}
#     except Exception as e:
#         return {'error': "Unexpected error: {}".format(e)}
#
#
# def task4(group_id=1):
#     try:
#         channels_in_group_list = list(Channels_in_group.objects.filter(group_id=group_id)) #list of all channells for asked group
#         total_budget = 10**10
#         ta = channels_in_group_list[0].group.channelgroup_TA
#         ta_in_channel_list = [TA_in_channel.objects.get(channel=i.channel, TA=ta) for i in channels_in_group_list]
#         chan_number = len(channels_in_group_list)
#         cp_list = [channel.user_CPM / 1000 if channel.user_CPM else ta_in_channel_list[i].default_CPM / 1000 for i, channel in enumerate(channels_in_group_list)]
#         views_split = [channel.channel_split_views for channel in channels_in_group_list if channel.channel_split_views]
#         budget_split_by_views = []
#         if views_split:
#             if len(views_split) != chan_number or sum(views_split) != 1:
#                 return {'error': 'Check views split'}
#             # count budget split based on views split
#             budget_split_by_views = get_split(
#                 [views_split_ch * cp_list_ch for views_split_ch, cp_list_ch in zip(views_split, cp_list)])
#
#         budget_split = budget_split_by_views or [channel.channel_split_budget for channel in channels_in_group_list if
#                         channel.channel_split_budget]
#         if budget_split:
#             if len(budget_split) != chan_number or round(sum(budget_split), 1) != 1:
#                 return {'error': 'Check budget split', 'budget_split': budget_split}
#             else:
#                 budget_list_max = [total_budget * ch_budget_p for ch_budget_p in budget_split]
#                 #check max channel budgets
#                 for number, channel in enumerate(channels_in_group_list):
#                     limit_max = channel.channel_budget_limit_max or channel.channel_show_limit_max * cp_list[number] if channel.channel_show_limit_max else None
#                     if limit_max:
#                         budget_list_var = [limit_max / budget_split[number] * ch_budget_p for ch_budget_p in budget_split]
#                         if sum(budget_list_var) < sum(budget_list_max):
#                             budget_list_max = budget_list_var
#                 #check for min channel budgets
#                 budget_list_min = [0 * ch_budget_p for ch_budget_p in budget_split]
#                 for number, channel in enumerate(channels_in_group_list):
#                     limit_min = channel.channel_budget_limit_min or channel.channel_show_limit_min * cp_list[number] if channel.channel_show_limit_min else None
#                     if limit_min:
#                         budget_list_var = [limit_min / budget_split[number] * ch_budget_p for ch_budget_p in budget_split]
#                         if sum(budget_list_var) > sum(budget_list_min):
#                             budget_list_min = budget_list_var
#                 if sum(budget_list_max) < sum(budget_list_min):
#                         return {'error': 'min budget for channels {} more than max budget for channels {}'.format(sum(budget_list_min), sum(budget_list_max))}
#
#                 r_fixed = channels_in_group_list[0].group.channelgroup_R_fixed
#                 #try to find min budget in 1000 steps
#                 STEPS = 1000
#                 # for i in range(int(budget_list_min[0]), int(budget_list_max[0])+1, int((budget_list_max[0] - budget_list_min[0]) / STEPS)):
#                 for i in range(int(budget_list_min[0]), int(budget_list_max[0]) + 1, 1):
#                     budget_list_cur = [i / budget_split[0] * ch_budget_p for ch_budget_p
#                                        in budget_split]
#                     views_list = [round(ch_budget / cp_list[i]) for i, ch_budget in enumerate(budget_list_cur)]
#                     r_list = [count_r(views_list[i], ta_in_channel_list[i]) for i in range(chan_number)]
#                     r = round(total_r(r_list), 3)
#                     if r >= r_fixed:
#                         return {'task': 4, 'min_budget': round(sum(budget_list_cur)), 'r': r, 'budget_split': budget_split,
#                                 'budget': round(sum(budget_list_cur)), 'views': views_list, 'views_split': get_split(views_list),
#                                 'r_perc': round(r * 100, 1), 'r_people': round(r * ta.TA_Size / 1000, 3)}
#                 return {'error': "sorry, can't find min budget for this R with TEST max lim for budget {}".format(total_budget)}
#         return {'error': 'check splits'}
#     except Exception as e:
#         return {'error': "Unexpected error: {}".format(e)}

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
