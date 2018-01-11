from .models import ChannelGroup, Channels_in_group, TA_in_channel
from itertools import product


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


def task1(group_id=1):
    try:
        channels_in_group_list = list(Channels_in_group.objects.filter(group_id=group_id)) #list of all channells for asked group
        total_budget = channels_in_group_list[0].group.channelgroup_budget
        ta = channels_in_group_list[0].group.channelgroup_TA
        ta_in_channel_list = [TA_in_channel.objects.get(channel=i.channel, TA=ta) for i in channels_in_group_list]
        chan_number = len(channels_in_group_list)
        cp_list = [channel.user_CPM / 1000 if channel.user_CPM else ta_in_channel_list[i].default_CPM / 1000 for i, channel in enumerate(channels_in_group_list)]
        views = []
        steps_number = 10**(6/chan_number)
        for number, channel in enumerate(channels_in_group_list):
            min_range = channel.channel_show_limit_min if channel.channel_show_limit_min else 0
            min_range = round(channel.channel_budget_limit_min / cp_list[number]) if channel.channel_budget_limit_min else min_range
            max_range = channel.channel_show_limit_max if channel.channel_show_limit_max else round((total_budget/cp_list[number]))
            max_range = round(channel.channel_budget_limit_max / cp_list[number]) if channel.channel_budget_limit_max else max_range
            step = int((max_range - min_range) / steps_number)
            views_for_channel = range(min_range, max_range + step, step)
            print(len(views_for_channel))
            if channel.channel_fixed_show:
                views_for_channel = [channel.channel_fixed_show]
            if channel.channel_fixed_budget:
                views_for_channel = [round(channel.channel_fixed_budget/cp_list[number])]
            views.append(views_for_channel)
        rmax = 0
        views_best = 0
        budget = 0
        for views_list in product(*views):
            if sum(views_list[i] * cp_list[i] for i in range(chan_number)) > total_budget:
                continue
            r_list = [count_r(views_list[i], ta_in_channel_list[i]) for i in range(chan_number)]
            r = total_r(r_list)
            if r > rmax:
                rmax = r
                budget = [views_list[i] * cp_list[i] for i in range(chan_number)]
                views_best = views_list
        if budget == 0:
            return {'error': "sorry, can't find answer with this params"}
        r = rmax
        return {'task': 1, 'r': r, 'budget_split': get_split(budget), 'budget': budget, 'views': views_best,
                'r_perc': round(r * 100, 1), 'r_people': round(r * ta.TA_Size / 1000, 3), 'views_split': get_split(views_best)}
    except Exception as e:
        return {'error': "Unexpected error: {}".format(e)}


def task2(group_id=1):
    try:
        channels_in_group_list = list(Channels_in_group.objects.filter(group_id=group_id)) #list of all channells for asked group
        total_budget = channels_in_group_list[0].group.channelgroup_budget
        ta = channels_in_group_list[0].group.channelgroup_TA
        ta_in_channel_list = [TA_in_channel.objects.get(channel=i.channel, TA=ta) for i in channels_in_group_list]
        chan_number = len(channels_in_group_list)
        cp_list = [channel.user_CPM / 1000 if channel.user_CPM else ta_in_channel_list[i].default_CPM / 1000 for i, channel in enumerate(channels_in_group_list)]
        views_split = [channel.channel_split_views for channel in channels_in_group_list if channel.channel_split_views]
        budget_split_by_views = []
        if views_split:
            if len(views_split) != chan_number or sum(views_split) != 1:
                return {'error': 'Check views split'}
            #count budget split based on views split
            budget_split_by_views = get_split([views_split_ch * cp_list_ch for views_split_ch, cp_list_ch in zip(views_split, cp_list)])

        budget_split = budget_split_by_views or [channel.channel_split_budget for channel in channels_in_group_list if channel.channel_split_budget]
        if budget_split:
            if len(budget_split) != chan_number or round(sum(budget_split), 1) != 1:
                return {'error': 'Check budget split', 'budget_split': budget_split}
            else:
                budget_list = [total_budget * ch_budget_p for ch_budget_p in budget_split]
                #check max channel budgets
                for number, channel in enumerate(channels_in_group_list):
                    limit_max = channel.channel_budget_limit_max or channel.channel_show_limit_max * cp_list[number] if channel.channel_show_limit_max else None
                    if limit_max:
                        budget_list_var = [limit_max / budget_split[number] * ch_budget_p for ch_budget_p in budget_split]
                        if sum(budget_list_var) < sum(budget_list):
                            budget_list = budget_list_var
                #check for min budgets
                for number, channel in enumerate(channels_in_group_list):
                    limit_min = channel.channel_budget_limit_min or channel.channel_show_limit_min*cp_list[number] if channel.channel_show_limit_min else None
                    if limit_min and limit_min > budget_list[number]:
                        return {'error': 'min budget for channel {} is more than possible budget split and max for other groups'.format(channel.channel.channel_name)}
                views_list = [round(ch_budget / cp_list[i]) for i, ch_budget in enumerate(budget_list)]
                r_list = [count_r(views_list[i], ta_in_channel_list[i]) for i in range(chan_number)]
                r = round(total_r(r_list), 3)
                return {'task': 2, 'r': r, 'budget_split': budget_split, 'budget': round(sum(budget_list)), 'views': views_list,
                        'views_split': get_split(views_list), 'r_perc': round(r * 100, 1), 'r_people': round(r * ta.TA_Size / 1000, 3)}
        return {'error': 'check splits'}
    except Exception as e:
        return {'error': "Unexpected error: {}".format(e)}

def task3(group_id=1):
    try:
        channels_in_group_list = list(Channels_in_group.objects.filter(group_id=group_id)) #list of all channells for asked group
        predicted_total_budget = max(a.channelgroup_budget for a in ChannelGroup.objects.all() if a.channelgroup_budget)
        predicted_total_budget = predicted_total_budget or 100000
        ta = channels_in_group_list[0].group.channelgroup_TA
        ta_in_channel_list = [TA_in_channel.objects.get(channel=i.channel, TA=ta) for i in channels_in_group_list]
        chan_number = len(channels_in_group_list)
        cp_list = [channel.user_CPM / 1000 if channel.user_CPM else ta_in_channel_list[i].default_CPM / 1000 for i, channel in enumerate(channels_in_group_list)]
        views = []
        steps_number = 10**(6/chan_number)
        for number, channel in enumerate(channels_in_group_list):
            min_range = channel.channel_show_limit_min if channel.channel_show_limit_min else 0
            min_range = round(channel.channel_budget_limit_min / cp_list[number]) if channel.channel_budget_limit_min else min_range
            max_range = channel.channel_show_limit_max if channel.channel_show_limit_max else round((predicted_total_budget/cp_list[number]))
            max_range = round(channel.channel_budget_limit_max / cp_list[number]) if channel.channel_budget_limit_max else max_range
            step = int((max_range - min_range) / steps_number)
            views_for_channel = range(min_range, max_range + step, step)
            if channel.channel_fixed_show:
                views_for_channel = [channel.channel_fixed_show]
            if channel.channel_fixed_budget:
                views_for_channel = [round(channel.channel_fixed_budget/cp_list[number])]
            views.append(views_for_channel)
        r_fixed = channels_in_group_list[0].group.channelgroup_R_fixed
        min_budget = 10**10
        views_best = 0
        budget = 0
        used_r = 0
        for views_split in product(*views):
            current_budget = sum(views_split[i] * cp_list[i] for i in range(chan_number))
            if current_budget > min_budget:
                continue
            r_list = [count_r(views_split[i], ta_in_channel_list[i]) for i in range(chan_number)]
            r = total_r(r_list)
            if r >= r_fixed:
                used_r = r
                min_budget = current_budget
                budget = [views_split[i] * cp_list[i] for i in range(chan_number)]
                views_best = views_split
        if budget == 0:
            return {'error': "sorry, can't find answer with this params"}
        r = used_r
        return {'task': 3, 'min_budget': min_budget, 'r': r, 'budget_split': get_split(budget), 'budget': sum(budget),
                'views': views_best, 'views_split': get_split(views_best), 'r_perc': round(r * 100, 1), 'r_people': round(r * ta.TA_Size / 1000, 3)}
    except Exception as e:
        return {'error': "Unexpected error: {}".format(e)}


def task4(group_id=1):
    try:
        channels_in_group_list = list(Channels_in_group.objects.filter(group_id=group_id)) #list of all channells for asked group
        total_budget = 10**10
        ta = channels_in_group_list[0].group.channelgroup_TA
        ta_in_channel_list = [TA_in_channel.objects.get(channel=i.channel, TA=ta) for i in channels_in_group_list]
        chan_number = len(channels_in_group_list)
        cp_list = [channel.user_CPM / 1000 if channel.user_CPM else ta_in_channel_list[i].default_CPM / 1000 for i, channel in enumerate(channels_in_group_list)]
        views_split = [channel.channel_split_views for channel in channels_in_group_list if channel.channel_split_views]
        budget_split_by_views = []
        if views_split:
            if len(views_split) != chan_number or sum(views_split) != 1:
                return {'error': 'Check views split'}
            # count budget split based on views split
            budget_split_by_views = get_split(
                [views_split_ch * cp_list_ch for views_split_ch, cp_list_ch in zip(views_split, cp_list)])

        budget_split = budget_split_by_views or [channel.channel_split_budget for channel in channels_in_group_list if
                        channel.channel_split_budget]
        if budget_split:
            if len(budget_split) != chan_number or round(sum(budget_split), 1) != 1:
                return {'error': 'Check budget split', 'budget_split': budget_split}
            else:
                budget_list_max = [total_budget * ch_budget_p for ch_budget_p in budget_split]
                #check max channel budgets
                for number, channel in enumerate(channels_in_group_list):
                    limit_max = channel.channel_budget_limit_max or channel.channel_show_limit_max * cp_list[number] if channel.channel_show_limit_max else None
                    if limit_max:
                        budget_list_var = [limit_max / budget_split[number] * ch_budget_p for ch_budget_p in budget_split]
                        if sum(budget_list_var) < sum(budget_list_max):
                            budget_list_max = budget_list_var
                #check for min channel budgets
                budget_list_min = [0 * ch_budget_p for ch_budget_p in budget_split]
                for number, channel in enumerate(channels_in_group_list):
                    limit_min = channel.channel_budget_limit_min or channel.channel_show_limit_min * cp_list[number] if channel.channel_show_limit_min else None
                    if limit_min:
                        budget_list_var = [limit_min / budget_split[number] * ch_budget_p for ch_budget_p in budget_split]
                        if sum(budget_list_var) > sum(budget_list_min):
                            budget_list_min = budget_list_var
                if sum(budget_list_max) < sum(budget_list_min):
                        return {'error': 'min budget for channels {} more than max budget for channels {}'.format(sum(budget_list_min), sum(budget_list_max))}

                r_fixed = channels_in_group_list[0].group.channelgroup_R_fixed
                #try to find min budget in 1000 steps
                STEPS = 1000
                # for i in range(int(budget_list_min[0]), int(budget_list_max[0])+1, int((budget_list_max[0] - budget_list_min[0]) / STEPS)):
                for i in range(int(budget_list_min[0]), int(budget_list_max[0]) + 1, 1):
                    budget_list_cur = [i / budget_split[0] * ch_budget_p for ch_budget_p
                                       in budget_split]
                    views_list = [round(ch_budget / cp_list[i]) for i, ch_budget in enumerate(budget_list_cur)]
                    r_list = [count_r(views_list[i], ta_in_channel_list[i]) for i in range(chan_number)]
                    r = round(total_r(r_list), 3)
                    if r >= r_fixed:
                        return {'task': 4, 'min_budget': round(sum(budget_list_cur)), 'r': r, 'budget_split': budget_split,
                                'budget': round(sum(budget_list_cur)), 'views': views_list, 'views_split': get_split(views_list),
                                'r_perc': round(r * 100, 1), 'r_people': round(r * ta.TA_Size / 1000, 3)}
                return {'error': "sorry, can't find min budget for this R with TEST max lim for budget {}".format(total_budget)}
        return {'error': 'check splits'}
    except Exception as e:
        return {'error': "Unexpected error: {}".format(e)}
