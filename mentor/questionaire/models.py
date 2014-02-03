from django.db import models
from django import forms
from mentor.users.models import User
from django.conf import settings as SETTINGS

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

class Questionaire(models.Model):
    questionaire_id = models.AutoField(primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)


    

    # User submited this form
    user = models.ForeignKey(User)

    # Questions
    student_name = models.CharField(max_length=30, blank=False) # Student name
    mentor_name = models.CharField(max_length=30, blank=False)      # Mentor name
    identity = models.CharField(max_length=2, blank=False)                      # Are you a Student or mentor(choice field/auto)

    primary_concern = models.TextField(blank=False)                 # What are your primary concerns?
    step_taken = models.TextField(blank=True)                       # Please share the steps you've taken to address these concerns (if any)
    support_from_MAPS = models.TextField(blank=True)                # What kind of support would be helpful from the MAPS team?
    
    follow_up_email = models.EmailField(null=True,blank=True)
    follow_up_phone = models.CharField(max_length=15,blank=True)
    follow_up_appointment = models.DateField(null=True,blank=True)


    def sendNotification(self):

        # Send a notification email to the person signed in
        if self.user is not None:
            to_user = self.user.username + '@' + SETTINGS.EMAIL_DOMAIN
            
            context_to_user = {
                "username" : self.user.username
            }

            context_to_psu_email_list = {
                "username" : self.user.username,
                "questionaire" : self,
            }

            # Send email to user
            text_content_to_user = render_to_string('questionaire/notification.txt', context_to_user)
            html_content_to_user = render_to_string('questionaire/notification.html', context_to_user)
            subject_to_user = "[MAPS Webform] Your response is submitted"

            msg_to_user = EmailMultiAlternatives(subject_to_user, text_content_to_user, SETTINGS.EMAIL_FROM, [to_user])
            msg_to_user.attach_alternative(html_content_to_user, "text/html")

            # Send email to PSU Email List
            text_content_psu_email_list = render_to_string('questionaire/notificationToPSU.txt', context_to_psu_email_list)
            html_content_psu_email_list = render_to_string('questionaire/notificationToPSU.html', context_to_psu_email_list)
            subject_to_psu_email_list = "[MAPS Webform] A MAPS Webform is submitted"

            msg = EmailMultiAlternatives(subject_to_psu_email_list, text_content_psu_email_list, SETTINGS.EMAIL_FROM, [SETTINGS.EMAIL_LIST] )
            msg.attach_alternative(html_content_psu_email_list, "text/html")
            return (msg.send() + msg_to_user.send())
        else:
            return 0

    class Meta:
        db_table = 'questionaire'
        ordering = ['created_on']
