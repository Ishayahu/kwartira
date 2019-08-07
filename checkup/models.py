from django.db import models
from django.conf import settings

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