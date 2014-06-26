from decimal import Decimal
from django import forms
from mentor.questionaire.models import Questionaire, PrimaryConcernChoice 
from datetime import date 

class USPhoneNumberMultiWidget(forms.MultiWidget):
    """
    A Widget that splits US Phone number input into three  boxes.
    """
    def __init__(self,attrs=None):
        widgets = (
            forms.TextInput(attrs={'size':'3','maxlength':'3', 'class':'phone form-control-noblock input-sm'}),
            forms.TextInput(attrs={'size':'3','maxlength':'3', 'class':'phone form-control-noblock input-sm'}),
            forms.TextInput(attrs={'size':'4','maxlength':'4', 'class':'phone form-control-noblock input-sm'}),
        )
        super(USPhoneNumberMultiWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value[0:3],value[3:6],value[6:10]]
        return [None,None,None]

    def value_from_datadict(self, data, files, name):
        values = super(USPhoneNumberMultiWidget, self).value_from_datadict(data, files, name)
        return u'%s%s%s' % tuple(values)


class QuestionaireForm(forms.ModelForm):
    STUDENT = 'ST'
    MENTOR = 'MT'
    IDENTITY_CHOICES = (
        (STUDENT, 'Student'),
        (MENTOR, 'Mentor'),
    )

    UNST_CHOICES = (
        ('FRINQ','FRINQ (Freshman Inquiry)'),
        ('SINQ','SINQ (Sophomore Inquiry)')
    )

    COURSE_TYPE_CHOICES = (
        ('HB','Hybrid'),
        ('OL','Online'),
        ('IP','In-person')
    )

    PRIMARY_CONCERN_CHOICES = PrimaryConcernChoice.objects.all()

    WHEN_CHOICES = (
        2*('In the past few days',),
        2*('In the last week',),
        2*('In the last two weeks',),
        2*('In the last month',),
        2*('Over a month ago',),
        2*("Don't know/Other",)
    )

    YN_CHOICES = (
        ('Y','Yes'),
        ('N','No')
    )

    NY_CHOICES = (
        (STUDENT,'Yes'),
        (MENTOR, 'No')
    )

    name = forms.CharField(label='Name',error_messages={'required':'Please enter your name'},required=True)
    student_ID = forms.CharField(label='Student ID#', required=False)
    student_name = forms.CharField(label='Name of student',required=False)
    mentor_name = forms.CharField(label='Name of FRINQ or SINQ mentor',required=False)
    UNST_course = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=UNST_CHOICES,
        label='I am currently enrolled in:',
        required=False
    )
    type_of_course = forms.ChoiceField(
        choices=COURSE_TYPE_CHOICES,
        label='Is your UNST course in-person, online or hybrid?',
        required=False
    )
    identity = forms.ChoiceField(
        choices=IDENTITY_CHOICES,
        label='Are you a student or a mentor?',
        widget=forms.RadioSelect(),
        required=True
    )
    on_behalf_of_student = forms.ChoiceField(
        choices=YN_CHOICES,
        label='Are you filling out this form on behalf of student?',
        widget=forms.RadioSelect(),
        required=False
    )
    primary_concern = forms.ModelMultipleChoiceField(
        widget=forms.widgets.CheckboxSelectMultiple(attrs={'class': 'control-label', 'style':'margin-bottom: 0px'}),
        queryset=PRIMARY_CONCERN_CHOICES,
        label='What are your primary concerns? (Check all that apply)',
        required=False,
    )
    primary_concern_other = forms.CharField(
        widget=forms.widgets.TextInput(attrs={'class': 'form-control input-sm'}),
        label="Other: ",
        required=False,
    )
    primary_concern_details = forms.CharField(
        widget=forms.widgets.Textarea(attrs={'rows':'3', }),
        label="Please provide us with some details about your primary concern(s):",
        required=False,
    )
    step_taken = forms.CharField(
        widget=forms.widgets.Textarea(attrs={'rows':'3', }),
        label="Please share the steps you've taken to address these concerns (if any)",
        required=False,
    )
    when_take_step = forms.ChoiceField(
        choices=WHEN_CHOICES,
        label='When did you take these steps?',
        required=False,
    )
    support_from_MAPS = forms.CharField(
        widget=forms.widgets.Textarea(attrs={'rows':'3'}),
        label="What kind of support would be helpful from the MAPS team?",
        required=False,
    )
    contact_who = forms.ChoiceField(
        choices=NY_CHOICES,
        label='Would you like us to respond directly to the student?',
        widget=forms.RadioSelect(),
        required=False,
    )
    follow_up_email = forms.EmailField(
        widget=forms.widgets.EmailInput,
        label='Email',
        required=False
    )
    follow_up_phone = forms.DecimalField(
        widget = USPhoneNumberMultiWidget,
        error_messages={'required':'Please insert an appropriate phone number'},
        label='Phone number',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(QuestionaireForm, self).__init__(*args, **kwargs)

        controls = ['primary_concern_details', 'name', 'student_ID', 'student_name', 'mentor_name', 'when_take_step', 'type_of_course', 'step_taken', 'when_take_step', 'support_from_MAPS', 'follow_up_email']
        for control in controls:
            self.fields[control].widget.attrs['class'] = 'form-control input-sm'

    def save(self, user, *args, **kwargs):
        """
        Overide the save method to input username automatically from
        CAS authentication information
        """

        self.instance.user = user
        post = super(QuestionaireForm, self).save(*args, **kwargs)
        post.sendNotification()

    def clean_on_behalf_of_student(self):
        # Since "identity" field is placed first under fields list in Meta class,
        # it will be saved first
        # It will guarantee self.cleaned_data.get("identity") to return an existing data
        on_behalf_of_student = self.cleaned_data.get("on_behalf_of_student")
        identity = self.cleaned_data.get("identity")

        if (identity == 'MT') and (not on_behalf_of_student):
            raise forms.ValidationError('Please answer this question')

        if (identity == 'ST'):
            on_behalf_of_student = ''

        return on_behalf_of_student

    def clean_student_ID(self):
        student_id = self.cleaned_data["student_ID"]
        if student_id == "":
            return None

        if len(str(student_id)) != 9:
            raise forms.ValidationError("Please enter a 9 digit student ID number")
        if set(student_id) - set("0123456789") != set():
            raise forms.ValidationError("Please enter a 9 digit student ID number")

        return student_id

    def clean_contact_who(self):
        contact_who = self.cleaned_data.get("contact_who")
        on_behalf_of_student = self.cleaned_data.get("on_behalf_of_student")
        identity = self.cleaned_data.get("identity")

        # Only when mentor fill out the form for student issue, we must
        # validate the contact_who field
        # Otherwise, leave it blank
        if (identity == 'MT') and (on_behalf_of_student == 'Y'):
            if (not contact_who):
                raise forms.ValidationError('Please answer this question')
            else:
                return contact_who
        else:
            return ''

    def clean_mentor_name(self):
        mentor_name = self.cleaned_data.get("mentor_name")
        identity = self.cleaned_data.get("identity")

        # Mentor name is required when student fill out the form.
        if (identity == 'ST') and (mentor_name == ''):
            raise forms.ValidationError("Please enter your mentor's name")

        return mentor_name

    def clean_student_name(self):
        student_name = self.cleaned_data.get("student_name")
        on_behalf_of_student = self.cleaned_data.get("on_behalf_of_student")
        identity = self.cleaned_data.get("identity")

        # Student name is required when mentor fills out the form on behalf of student.
        if (identity == 'MT') and (on_behalf_of_student == 'Y') and (student_name == ''):
            raise forms.ValidationError('Please enter student name')

        return student_name

    def clean_UNST_course(self):
        UNST_course = self.cleaned_data.get("UNST_course")
        on_behalf_of_student = self.cleaned_data.get("on_behalf_of_student")
        identity = self.cleaned_data.get("identity")

        # UNST course is required when student is filling out the form or mentor fill out the form for student
        if ((identity == "ST") or (on_behalf_of_student == "Y")) and (UNST_course == ''):
            raise forms.ValidationError('Please answer this question')

        return UNST_course

    def clean_primary_concern(self):
        primary_concern_other = self.cleaned_data.get("primary_concern_other")
        primary_concern = self.cleaned_data.get("primary_concern")

        if (primary_concern_other == '' and len(primary_concern) == 0):
            raise forms.ValidationError('Please answer this question')

        return primary_concern

    def clean_when_take_step(self):
        step_taken = self.cleaned_data.get("step_taken")
        when_take_step = self.cleaned_data.get("when_take_step")

        if (step_taken == ''):
            return ''
        else:
            return when_take_step

    def clean_type_of_course(self):
        UNST_course = self.cleaned_data.get("UNST_course")
        type_of_course = self.cleaned_data.get("type_of_course")

        if (UNST_course == 'FRINQ'):
            return ''
        else:
            return type_of_course

    def clean(self):
        cleaned_data = super(QuestionaireForm, self).clean()

        name = cleaned_data.get("name")
        student_name = cleaned_data.get("student_name")
        mentor_name = cleaned_data.get("mentor_name")
        on_behalf_of_student = cleaned_data.get("on_behalf_of_student")
        identity = cleaned_data.get("identity")

        if identity == 'ST':
            # Student is filling out the form, pop out name and assign that value to student_name
            cleaned_data.pop("name", None)
            cleaned_data["student_name"] = name
        elif identity == 'MT':
            # Mentor is filling out the form, pop out name and assign that value to mentor_name
            cleaned_data.pop("name", None)
            cleaned_data["mentor_name"] = name

        # Make sure that user enters at least one method of follow-up
        email = cleaned_data.get("follow_up_email")
        phone = cleaned_data.get("follow_up_phone")

        if not email and not phone :
            self.cleaned_data.pop("follow_up_email", None)
            self.cleaned_data.pop("follow_up_phone", None)
            self._errors.setdefault('follow_up_phone', self.error_class()).append("Fill in at least one method to follow-up method")

        return cleaned_data

    class Meta:
        model = Questionaire
        fields = (
            # The order of fields below will dictate the order of data is being saved.
            'identity',
            'on_behalf_of_student',
            'student_name',
            'student_ID',
            'mentor_name',
            'UNST_course',
            'type_of_course',
            'primary_concern_other',
            'primary_concern',
            'step_taken',
            'when_take_step',
            'support_from_MAPS',
            'contact_who',
            'follow_up_email',
            'follow_up_phone',
            'primary_concern_details',
        )


class DownloadResponseForm(forms.Form):
    start_date = forms.DateField(
        label="Start Date: ",
        required=True,
    )

    end_date = forms.DateField(
        label="End Date: ",
        required=True,
    )

    def clean(self):
        cleaned_data = super(DownloadResponseForm, self).clean()

        try:
            start_date = cleaned_data['start_date']
            end_date = cleaned_data['end_date']
        except KeyError:
            raise forms.ValidationError("Fill in the required dates.")

        if end_date < start_date:
            raise forms.ValidationError("End Date can't smaller then Start Date.")

        return cleaned_data
