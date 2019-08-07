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
    for v in visits:
        print(v)
    visits_dates = [v.date for v in visits]
    print(visits_dates)
    start_date = timezone.now().date()
    end_date = start_date - datetime.timedelta(days = count)
    result = []
    current_date = start_date

    # день недели в виде числа, понедельник - 0, воскресенье - 6. Исключаем 4,5 - пятница и шабат
    # print("getting visites from {} to {}".format(start_date, end_date))
    while current_date >= end_date:
        # print("\tprocessing {}".format(current_date))
        if current_date.weekday() not in [4,5]:
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
    import datetime
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    visit, created = Visit.objects.get_or_create(date = date, user = user)
    # if obj:
    #     visit = obj
    # else:
    #     visit = created
    if visit.user == user or user.pk in ADMINS:
        if request.method == 'POST':
            form = VisitleForm(request.POST, instance=visit)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('visit_show_for_user', kwargs={'count': 7 * 4, 'user_id': user.pk}))
        else:
            form = VisitleForm(instance=visit)
        return render(request, 'checkup/add.html', {'form': form})
    else:
        return HttpResponseNotFound("Visit does not exist")

@login_required
def index(request):

    users = User.objects.all()
    for user in users:
        user.show_url_name = 'visit_show_default_for_user'
        user.to_string = "{} {}".format(user.last_name, user.first_name)
    return render(request, 'checkup/list.html', {'items': users})


# from django.views import View
#
# class VisitDetail(DetailView):
#     model = Visit
#
#     def get_context_data (self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         context['book_list'] = Visit.objects.all()
#         return context