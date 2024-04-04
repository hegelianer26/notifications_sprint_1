from django.contrib import admin
from .models import EmailTemplate, EmailCampaign
import json
import requests
import uuid
from .tasks import send_mail_once
from celery import shared_task
import os
from mail.tasks import send_mail_once
from celery import current_app


class EmailCampaignAdmin(admin.ModelAdmin):
    def send_emails(self, request, queryset):
        message = []
        for campaign in queryset:
            message.append({
                "user_groups": campaign.user_groups,
                "sender": campaign.template.sender,
                "content": campaign.template.content,
                "subject": campaign.template.subject,
                "uuid": str(uuid.uuid4()),
            })
            
        current_app.send_task('mail.tasks.send_mail_once', args=message, eta=campaign.time)

    send_emails.short_description = "Send Emails"
    actions = [send_emails]

admin.site.register(EmailCampaign, EmailCampaignAdmin)
admin.site.register(EmailTemplate)
