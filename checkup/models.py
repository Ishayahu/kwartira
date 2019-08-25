from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class TwoPeopleRoom(models.Model):
    number = models.IntegerField()
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null = True, blank = True, related_name='first2')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null = True, blank = True, related_name='second2')
    def __str__(self):
        return str(self.number)
    def people_count(self):
        return 2
    # def as_table_row(self):
    #     user1 = User.objects.get(id=self.user1)
    #     if user1:
    #         user1_fio = "{} {}".format(user1.last_name, user1.first_name)
    #     else:
    #         user1_fio = "-"*10
    #     user2 = User.objects.get(id=self.user2)
    #     if user2:
    #         user2_fio = "{} {}".format(user2.last_name, user2.first_name)
    #     else:
    #         user2_fio = "-"*10
    #
    #     return """
    #     <tr>
    #         <td  rowspan='2'>{number}</td>
    #         <td>{user1_fio}</td>
    #     </tr>
    #     <tr>
    #         <td>{user2_fio}</td>
    #     </tr>
    #     """.format(number = self.number, user1_fio = user1_fio, user2_fio = user2_fio)

class ThreePeopleRoom(models.Model):
    number = models.IntegerField()
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null = True, blank = True, related_name='first3')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null = True, blank = True, related_name='second3')
    user3 = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null = True, blank = True, related_name='third3')
    def __str__(self):
        return str(self.number)
    def people_count(self):
        return 3
    # def as_table_row(self):
        # user1 = User.objects.get(id=self.user1)
        # if user1:
        #     user1_fio = "{} {}".format(user1.last_name, user1.first_name)
        # else:
        #     user1_fio = "-"*10
        # user2 = User.objects.get(id=self.user2)
        # if user2:
        #     user2_fio = "{} {}".format(user2.last_name, user2.first_name)
        # else:
        #     user2_fio = "-"*10
        # user3 = User.objects.get(id=self.user3)
        # if user3:
        #     user3_fio = "{} {}".format(user3.last_name, user3.first_name)
        # else:
        #     user3_fio = "-"*10
        #
        # return """
        # <tr>
        #     <td  rowspan='3'>{number}</td>
        #     <td>{user1_fio}</td>
        # </tr>
        # <tr>
        #     <td>{user2_fio}</td>
        # </tr>
        # <tr>
        #     <td>{user3_fio}</td>
        # </tr>
        # """.format(number = self.number, user1_fio = user1_fio, user2_fio = user2_fio, user3_fio = user3_fio)

class OnePeopleRoom(models.Model):
    number = models.IntegerField()
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null = True, blank = True, related_name='first1')
    def __str__(self):
        return str(self.number)
    def people_count(self):
        return 1
    # def as_table_row(self):
    #     user1 = User.objects.get(id=self.user1.)
    #     return """<tr>
    #         <td>{number}</td>
    #         <td>{user1_fio}</td>
    #     </tr>""".format(number = self.number, user1_fio = "{} {}".format(user1.last_name, user1.first_name))


# Create your models here.
class Visit(models.Model):
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    shacharit = models.CharField(max_length = 200, blank=True, null=True)
    mincha = models.CharField(max_length = 200, blank=True, null=True)
    maariv = models.CharField(max_length = 200, blank=True, null=True)
    learning = models.CharField(max_length = 200, blank=True, null=True)
    missing = models.BooleanField(default = False)

    def __str__(self):
        return "[{}] {}@{}: {} {} {} {} {}".format(self.pk, self.user, self.date, self.shacharit, self.mincha, self.maariv, self.learning,
                                                   self.missing)

    def status(self):
        if self.date.weekday() == 5:  # шабат
            status = None
            if not self.shacharit:
                status = 'red'
            elif self.shacharit in "OoОо":
                status = 'orange'
            elif self.shacharit == '-':
                status = 'lime'
            elif self.shacharit:
                status = 'green'
            return "<span class='{} square'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>".format(status)
        elif self.date.weekday() == 4:  # пятница. По умолчанию учиться и не надо, поэтому отображается так
            status_learning_css = "LightYellow"
            # status_davening_css = "LightYellow"
        else:  # остальные дни. По умолчанию учиться надо
            status_learning_css = "red"


        if self.learning:
            status_learning_css = "green"

        status_davening_css = "red"
        davening_count = sum([bool(x) for x in (self.shacharit, self.mincha, self.maariv)])
        if davening_count==3:
            status_davening_css = "green"
        elif davening_count ==2:
            status_davening_css = "yellow"
        elif davening_count == 1:
            status_davening_css = "orange"
        status_learning = "<span class='{} square'>&nbsp;&nbsp;&nbsp;&nbsp;</span>".format(status_learning_css)
        status_davening = "<span class='{} square'>&nbsp;&nbsp;&nbsp;&nbsp;</span>".format(status_davening_css)
        return "{}/{}".format(status_learning, status_davening)
    def score(self):

        if self.date.weekday() == 5:  # шабат
            if not self.shacharit:
                return 1
            if self.shacharit in "OoОо":
                return 0.5
            elif self.shacharit == '-':
                return 0.1
            elif self.shacharit:
                return 0
        # остальные дни. По умолчанию учиться надо, кроме пятница
        result = 4
        if self.date.weekday() == 4:
            result = 3
        davening_count = sum([bool(x) for x in (self.shacharit, self.mincha, self.maariv)])
        result -= davening_count
        result -= 0 if self.learning else 1
        return result

class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    untill = models.DateField(blank = True, null = True)
    def __str__(self):
        return "{} {}".format(self.user,self.untill)