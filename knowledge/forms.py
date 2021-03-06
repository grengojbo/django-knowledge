# -*- mode: python; coding: utf-8; -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import ReCaptchaField
from knowledge import settings
from knowledge.models import Question, Response, Category

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

OPTIONAL_FIELDS = ['alert', 'categories', 'phone_number']
OPTIONAL_FIELDS_OFFICE = ['alert', 'categories', 'phone_number', 'parking', 'chbox1', 'chbox2']

__todo__ = """
This is serious badness. Really? Functions masquerading as
clases? Lame. This should be fixed. Sorry.
                                                    ~bryan
"""


def QuestionForm(user, *args, **kwargs):
    """
    Build and return the appropriate form depending
    on the status of the passed in user.
    """

    if user.is_anonymous():
        if not settings.ALLOW_ANONYMOUS:
            return None
        else:
            selected_fields = ['name', 'email', 'title', 'body', 'phone_number']
    else:
        selected_fields = ['user', 'title', 'body', 'status', 'phone_number']

    if settings.ALERTS:
        selected_fields += ['alert']

    class _QuestionForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(_QuestionForm, self).__init__(*args, **kwargs)

            for key in self.fields:
                if not key in OPTIONAL_FIELDS:
                    self.fields[key].required = True

            # hide the internal status for non-staff
            qf = self.fields.get('status', None)
            if qf and not user.is_staff:
                choices = list(qf.choices)
                choices.remove(('internal', _('Internal')))
                qf.choices = choices

            # a bit of a hack...
            # hide a field, and use clean to force
            # a specific value of ours
            for key in ['user']:
                qf = self.fields.get(key, None)
                if qf:
                    qf.widget = qf.hidden_widget()
                    qf.required = False

        # honey pot!
        #phone_number = forms.CharField(label=_('Phone number'), required=False)
        # if user.is_anonymous():
        #     captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'ru'})

        def clean_user(self):
            return user

        class Meta:
            model = Question
            fields = selected_fields

    return _QuestionForm(*args, **kwargs)


def QuestionAskForm(user, *args, **kwargs):
    """
    Build and return the appropriate form depending
    on the status of the passed in user.
    """
    logger.debug(">>>>> QuestionAskForm ")
    #logger.debug("lot_form: {0}".format(f))
    if user.is_anonymous():
        if not settings.ALLOW_ANONYMOUS:
            return None
        else:
            selected_fields = ['name', 'email', 'company', 'body', 'categories', 'phone_number']
    else:
        selected_fields = ['user', 'company', 'body', 'categories', 'phone_number']

    if settings.ALERTS:
        selected_fields += ['alert']

    class _QuestionAskForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(_QuestionAskForm, self).__init__(*args, **kwargs)

            for key in self.fields:
                if not key in OPTIONAL_FIELDS:
                    self.fields[key].required = True

            # hide the internal status for non-staff
            qf = self.fields.get('status', None)
            if qf and not user.is_staff:
                choices = list(qf.choices)
                choices.remove(('internal', _('Internal')))
                qf.choices = choices

            # a bit of a hack...
            # hide a field, and use clean to force
            # a specific value of ours
            for key in ['user']:
                qf = self.fields.get(key, None)
                if qf:
                    qf.widget = qf.hidden_widget()
                    qf.required = False

        # honey pot!
        #phone_number = forms.CharField(label=_('Phone number'), required=False)
        if user.is_anonymous():
            captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'ru'})
        #categories = forms.MultipleChoiceField(choices=CAT_CHOICES, required=True)
        #categories = forms.ChoiceField(choices=Category.objects.values_list('id','title'), required=True)
        #categories = forms.MultipleHiddenInput(choices=Category.objects.all())
        #categories = forms.HiddenInput(initial=2)

        # attachment = forms.FileField(required=False,
        # label=_('Attach File'),
        # help_text=_('You can attach a file such as a document or screenshot to this ticket.'),
        # )
        #
        def clean_user(self):
            return user
        # def save(self, user):
        # files = []
        #         if self.cleaned_data['attachment']:
        #             import mimetypes
        #             file = self.cleaned_data['attachment']
        #             filename = file.name.replace(' ', '_')
        #             a = Attachment(
        #                 followup=f,
        #                 filename=filename,
        #                 mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
        #                 size=file.size,
        #                 )
        #             a.file.save(file.name, file, save=False)
        #             a.save()
        #
        #             if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
        #                 # Only files smaller than 512kb (or as defined in
        #                 # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
        #                 files.append(a.file.path)
        #

        class Meta:
            model = Question
            fields = selected_fields

    return _QuestionAskForm(*args, **kwargs)


def ShopAskForm(user=None, *args, **kwargs):
    """
    Build and return the appropriate form depending
    on the status of the passed in user.
    """
    logger.debug(">>>>> ShopAskForm ")
    #logger.debug("lot_form: {0}".format(f))
    if user.is_anonymous():
        if not settings.ALLOW_ANONYMOUS:
            return None
        else:
            selected_fields = ['name', 'email', 'activities', 'body', 'phone_number', 'company', 'trading', 'areea_leasse', 'date_leasse', 'range_of_goods', 'trademarks']
    else:
        selected_fields = ['user', 'activities',  'body', 'phone_number', 'company', 'trading', 'areea_leasse', 'date_leasse', 'range_of_goods', 'trademarks']

    if settings.ALERTS:
        selected_fields += ['alert']

    class _ShopAskForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(_ShopAskForm, self).__init__(*args, **kwargs)

            for key in self.fields:
                if not key in OPTIONAL_FIELDS:
                    self.fields[key].required = True

            # hide the internal status for non-staff
            qf = self.fields.get('status', None)
            if qf and not user.is_staff:
                choices = list(qf.choices)
                choices.remove(('internal', _('Internal')))
                qf.choices = choices

            # a bit of a hack...
            # hide a field, and use clean to force
            # a specific value of ours
            for key in ['user']:
                qf = self.fields.get(key, None)
                if qf:
                    qf.widget = qf.hidden_widget()
                    qf.required = False

            # self.fields['title'] = self.fields.get('title', title)
            # self.fields['categories'] = self.fields.get('categories', curent_cat)
            logger.debug("FIELD title: {0}".format(self.fields.get('title', None)))
            logger.debug("FIELD categories: {0}".format(self.fields.get('categories', None)))
            # logger.debug("FIELD initial: {0}".format(initial))

        # honey pot!
        #phone_number = forms.CharField(label=_('Phone number'), required=False)
        if user.is_anonymous():
            captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'ru'})
        #categories = forms.MultipleChoiceField(choices=CAT_CHOICES, required=True)
        #categories = forms.ChoiceField(choices=Category.objects.values_list('id','title'), required=True)
        #categories = forms.MultipleHiddenInput(choices=Category.objects.all())
        #categories = forms.HiddenInput(initial=2)

        # attachment = forms.FileField(required=False,
        # label=_('Attach File'),
        # help_text=_('You can attach a file such as a document or screenshot to this ticket.'),
        # )
        #
        def clean_user(self):
            return user
        # def save(self, user):
        # files = []
        #         if self.cleaned_data['attachment']:
        #             import mimetypes
        #             file = self.cleaned_data['attachment']
        #             filename = file.name.replace(' ', '_')
        #             a = Attachment(
        #                 followup=f,
        #                 filename=filename,
        #                 mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
        #                 size=file.size,
        #                 )
        #             a.file.save(file.name, file, save=False)
        #             a.save()
        #
        #             if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
        #                 # Only files smaller than 512kb (or as defined in
        #                 # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
        #                 files.append(a.file.path)
        #

        class Meta:
            model = Question
            fields = selected_fields

    return _ShopAskForm(*args, **kwargs)


def OfficesAskForm(user=None, *args, **kwargs):
    """
    Build and return the appropriate form depending
    on the status of the passed in user.
    """
    logger.debug(">>>>> OfficesAskForm ")
    #logger.debug("lot_form: {0}".format(f))
    if user.is_anonymous():
        if not settings.ALLOW_ANONYMOUS:
            return None
        else:
            selected_fields = ['name', 'email', 'activities', 'body', 'phone_number', 'company', 'trading', 'areea_leasse', 'floor', 'parking', 'chbox1', 'chbox2']
    else:
        selected_fields = ['user', 'activities',  'body', 'phone_number', 'company', 'trading', 'areea_leasse', 'floor', 'parking', 'chbox1', 'chbox2']

    if settings.ALERTS:
        selected_fields += ['alert']



    class _OfficesAskForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(_OfficesAskForm, self).__init__(*args, **kwargs)

            for key in self.fields:
                if not key in OPTIONAL_FIELDS_OFFICE:
                    self.fields[key].required = True

            # hide the internal status for non-staff
            qf = self.fields.get('status', None)
            if qf and not user.is_staff:
                choices = list(qf.choices)
                choices.remove(('internal', _('Internal')))
                qf.choices = choices

            # a bit of a hack...
            # hide a field, and use clean to force
            # a specific value of ours
            for key in ['user']:
                qf = self.fields.get(key, None)
                if qf:
                    qf.widget = qf.hidden_widget()
                    qf.required = False

            # self.fields['title'] = self.fields.get('title', title)
            # self.fields['categories'] = self.fields.get('categories', curent_cat)
            logger.debug("FIELD title: {0}".format(self.fields.get('title', None)))
            logger.debug("FIELD categories: {0}".format(self.fields.get('categories', None)))
            # logger.debug("FIELD initial: {0}".format(initial))


        if user.is_anonymous():
            captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'ru'})

        def clean_user(self):
            return user

        class Meta:
            model = Question
            fields = selected_fields

    return _OfficesAskForm(*args, **kwargs)

def ResponseForm(user, question, *args, **kwargs):
    """
    Build and return the appropriate form depending
    on the status of the passed in user and question.
    """

    if question.locked:
        return None

    if not settings.FREE_RESPONSE and not \
            (user.is_staff or question.user == user):
        return None

    if user.is_anonymous():
        if not settings.ALLOW_ANONYMOUS:
            return None
        else:
            selected_fields = ['name', 'email']
    else:
        selected_fields = ['user']

    selected_fields += ['body', 'question']

    if user.is_staff:
        selected_fields += ['status']

    if settings.ALERTS:
        selected_fields += ['alert']

    class _ResponseForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(_ResponseForm, self).__init__(*args, **kwargs)

            for key in self.fields:
                if not key in OPTIONAL_FIELDS:
                    self.fields[key].required = True

            # a bit of a hack...
            for key in ['user', 'question']:
                qf = self.fields.get(key, None)
                if qf:
                    qf.widget = qf.hidden_widget()
                    qf.required = False

        # honey pot!
        if user.is_anonymous():
            captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'ru'})

        def clean_user(self):
            return user

        def clean_question(self):
            return question

        class Meta:
            model = Response
            fields = selected_fields

    return _ResponseForm(*args, **kwargs)
