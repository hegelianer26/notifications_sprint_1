from django.db import models
from tinymce.models import HTMLField

periodicity_choices = [
    ("W", "Weekly"),
    ("OT", "Once")
]


class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    sender = models.CharField(max_length=200)
    content = HTMLField()

    def __str__(self):
        return self.name


class EmailCampaign(models.Model):
    name = models.CharField(max_length=100)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    periodicity = models.CharField(max_length=2, choices=periodicity_choices)
    time = models.DateTimeField()
    user_groups = models.CharField(max_length=100, default="basic")
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
