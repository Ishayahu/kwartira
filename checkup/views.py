# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.views.generic import DetailView
from checkup.models import *
from checkup.forms import *
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import datetime


ADMINS = (1,)
@login_required
def visit_add(request):
    user = request.user
    if request.method == 'POST':
        form = VisitleForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['user']!=user:
                form = VisitleForm(initial={'user': user, 'date': timezone.now()})
                return render(request, 'checkup/add.html', {'form': form, 'error_messages': ["Отмечаться можно только за себя",]})
            allready = Visit.objects.filter(user = user).filter(date = form.cleaned_data['date'])
            if allready:
                form = VisitleForm(initial={'user': user, 'date': timezone.now()})
                return render(request, 'checkup/add.html', {'form': form, 'error_messages': ["Такая дата уже была введена. Если хотите изменить значение - откройте её и отредактируйте",]})
            form.save()
            return HttpResponseRedirect(reverse('visit_show_for_user', kwargs={'count': 7*4, 'user_id': user.pk}))
    else:
        form = VisitleForm(initial={'user': user, 'date': timezone.now()})
    return render(request, 'checkup/add.html', {'form': form})

@login_required
def shabat_add(request):
    user = request.user
    if user.pk not in ADMINS:
        return HttpResponseNotFound("Только для одминов")

    users = User.objects.all()
    for user in users:
        user.show_url_name = 'visit_show_default_for_user'
        user.to_string = "{} {}".format(user.last_name, user.first_name)

    if request.method == 'POST':
        print(request.POST["shabat_date"])
        date = datetime.datetime.strptime(request.POST['shabat_date'], '%Y-%m-%d')
        print(date)
        if date.weekday() != 5:
            return HttpResponseNotFound("Не шабат")
        for user in users:
            a = request.POST
            if str(user.pk) in request.POST:
                visit, created = Visit.objects.get_or_create(date = date, user = user)
                if not visit.missing:  # чтобы случайно не отметить того, кого не было
                    visit.shacharit = request.POST[str(user.pk)]
                    visit.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        last_shabat = timezone.datetime.now()
        while last_shabat.weekday() != 5:
            last_shabat = last_shabat - datetime.timedelta(days = 1)
        return render(request, 'checkup/shabat_add.html', {'users': users, 'last_shabat': last_shabat.strftime("%Y-%m-%d")})


@login_required
def visit_show_for_user(request,count,user_id):
    count = int(count)
    class NotMarkedDay:
        def __init__(self,date):
            self.date = date
        def __str__(self):
            return str(self.date)
        def date_str(self):
            return self.date.isoformat()
        def status (self):

            if self.date.weekday() == 5:  # шабат
                status = 'red'
                return "<span class='{} square'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>".format(status)
            elif self.date.weekday() == 4:  # пятница. По умолчанию учиться и не надо, поэтому отображается так
                status_learning_css = "LightYellow"
            else:  # остальные дни. По умолчанию учиться надо
                status_learning_css = "red"
            status_davening_css = "red"
            status_learning = "<span class='{} square'>&nbsp;&nbsp;&nbsp;&nbsp;</span>".format(status_learning_css)
            status_davening = "<span class='{} square'>&nbsp;&nbsp;&nbsp;&nbsp;</span>".format(status_davening_css)
            return "{}/{}".format(status_learning, status_davening)

    user = get_object_or_404(User,pk = int(user_id))
    one_day = datetime.timedelta(days = 1)


    if request.method == 'POST':
        form = FromToForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            current_date = start_date
            # print("getting visites from {} to {}".format(start_date, end_date))
            while current_date <= end_date:
                # print("\tprocessing {}".format(current_date))
                visit,created = Visit.objects.get_or_create(date = current_date, user = user)
                # print("\t\t{} {}".format(visit, created))
                visit.missing = True
                visit.save()
                current_date += one_day
    form = FromToForm()

    visits = Visit.objects.filter(user=user).order_by('-date')[:count]
    # for v in visits:
        # print(v)
    visits_dates = [v.date for v in visits]
    # print(visits_dates)
    start_date = timezone.now().date()
    end_date = start_date - datetime.timedelta(days = count)
    result = []
    current_date = start_date

    # день недели в виде числа, понедельник - 0, воскресенье - 6. Исключаем 4,5 - пятница и шабат
    # print("getting visites from {} to {}".format(start_date, end_date))
    while current_date >= end_date:
        # Убрал это, так как нужна информация и по шабату, просто отображать её буду по другому
        # if current_date.weekday() not in [4,5]:

        if current_date in visits_dates:
            # print("\t\tappended Visit")
            result.append(visits[visits_dates.index(current_date)])
        else:
            # print("\t\tappended NotMarkedDay")
            result.append(NotMarkedDay(current_date))
        current_date = current_date - one_day

    return render(request, 'checkup/last_visits_for_user.html', {'visits': result, 'user': user, 'form': form})

@login_required
def visit_show_by_id(request,visit_id):
    user = request.user
    visit = Visit.objects.get(pk=visit_id)
    if visit.user == user or user.pk in ADMINS:
        if request.method == 'POST':
            form = VisitleForm(request.POST, instance=visit)
            if visit.date.weekday() != 5 or (visit.date.weekday() == 5 and user.pk in ADMINS):  # шабат только админ вносит
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse('visit_show_for_user', kwargs={'count': 7 * 4, 'user_id': user.pk}))
        else:
            form = VisitleForm(instance=visit)
        return render(request, 'checkup/add.html', {'form': form})
    else:
        return HttpResponseNotFound("Visit does not exist")

@login_required
def visit_show_by_date(request,date):
    user = request.user
    # import datetime
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    if request.method == 'POST':
        form = VisitleForm(request.POST)
        if form.is_valid():
            if user.pk in ADMINS:
                # то мы можем редактировать любую дату для любого пользователя
                visit, created = Visit.objects.get_or_create(date = date, user = form.cleaned_data['user'])
            elif date.weekday() == 5:
                return HttpResponseNotFound("Отмечать молитвы в шабат может только администратор")
            else:
                # можем редактировать только свои записи
                visit, created = Visit.objects.get_or_create(date = date, user = user)
            visit.shacharit = form.cleaned_data['shacharit']
            visit.mincha = form.cleaned_data['mincha']
            visit.maariv = form.cleaned_data['maariv']
            visit.learning = form.cleaned_data['learning']
            visit.missing = form.cleaned_data['missing']
            visit.save()
            return HttpResponseRedirect(reverse('visit_show_for_user', kwargs = {'count': 7 * 4, 'user_id': user.pk}))
    else:
        form = VisitleForm(initial = {'date': date, 'user': user})
        return render(request, 'checkup/add.html', {'form': form})

@login_required
def index(request):

    users = User.objects.all()
    user2room,_ = make_room_dict()
    print(user2room)
    count = 7*4
    for user in users:
        user.show_url_name = 'visit_show_default_for_user'
        user.to_string = "{} {}".format(user.last_name, user.first_name)

        visits = Visit.objects.filter(user = user).order_by('-date')[:count]
        score = 0
        start_date = timezone.now().date()
        end_date = start_date - datetime.timedelta(days = count)
        current_date = start_date
        visits_dates = [v.date for v in visits]
        one_day = datetime.timedelta(days = 1)
        while current_date >= end_date:
            if current_date in visits_dates:
                score += visits[visits_dates.index(current_date)].score()
            else:
                if current_date.weekday() == 5:
                    score += 1
                elif current_date.weekday() == 4: # пятница
                    score += 3
                else:
                    score += 4
            current_date = current_date - one_day
        user.score = score
        # интервал рейтинга видимо от 0 до 100. опытным путём выяснилось, что менятьнадо зелёный цвет: #ff1dff
        # средние два значения от максимума 255 до 0. Итого на один бал:
        user.score_color_code = "#ff{:02x}ff".format((round(255-score*2.55)))
        user.room_number = user2room.get(user,None)

    return render(request, 'checkup/list.html', {'items': users})

def make_room_dict():
    one = OnePeopleRoom.objects.all()
    two = TwoPeopleRoom.objects.all()
    three = ThreePeopleRoom.objects.all()
    user2room = dict()
    number2room = dict()
    for room in one:
        user2room[room.user1] = room.number
    for room in two:
        user2room[room.user1] = room.number
        user2room[room.user2] = room.number
    for room in three:
        user2room[room.user1] = room.number
        user2room[room.user2] = room.number
        user2room[room.user3] = room.number

    for room in one:
        number2room[room.number] = room
    for room in two:
        number2room[room.number] = room
    for room in three:
        number2room[room.number] = room


    return user2room, number2room

def rooms(request):
    _,number2room = make_room_dict()
    result = []
    today = timezone.now().date()
    for key in sorted(number2room.keys()):
        room = number2room[key]
        user = room.user1
        if user:
            future_missings = Visit.objects.filter(user = user).filter(date__gte = today).filter(missing = True)
            missings = [str(d.date) for d in future_missings]
            if missings:
                user.style = 'yellow'
                user.missing = missings

            try:
                userprofile = UserProfile.objects.get(user = user)
                if userprofile.untill:
                    user.style = 'red'
                    user.untill = userprofile.untill
            except UserProfile.DoesNotExist:
                pass
        try:
            user = room.user2
            if user:
                future_missings = Visit.objects.filter(user = user).filter(date__gte = today).filter(missing = True)
                missings = [str(d.date) for d in future_missings]
                if missings:
                    user.style = 'yellow'
                    user.missing = missings

                try:
                    userprofile = UserProfile.objects.get(user = user)
                    if userprofile.untill:
                        user.style = 'red'
                        user.untill = userprofile.untill
                except UserProfile.DoesNotExist:
                    pass
        except:
            pass
        try:
            user = room.user3
            if user:
                future_missings = Visit.objects.filter(user = user).filter(date__gte = today).filter(missing = True)
                missings = [str(d.date) for d in future_missings]
                if missings:
                    user.style = 'yellow'
                    user.missing = missings

                try:
                    userprofile = UserProfile.objects.get(user = user)

                    if userprofile.untill:
                        user.style = 'red'
                        user.untill = userprofile.untill
                except UserProfile.DoesNotExist:
                    pass
        except:
            pass
        result.append(room)
    # print(result)
    return render(request, 'checkup/rooms.html', {'rooms': result})

def room_show(request, room_number):
    _,number2room = make_room_dict()
    room = number2room[int(room_number)]
    forms = {1: OneRoomForm, 2: TwoRoomForm, 3: ThreeRoomForm}
    roomform = forms[room.people_count()]
    if request.method == 'POST':
        form = roomform(request.POST, instance = room)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('rooms'))
    else:
        form = roomform(instance = room)
        return render(request, 'checkup/add.html', {'form': form})
