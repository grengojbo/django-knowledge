# -*- mode: python; coding: utf-8; -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import ReCaptchaField
from knowledge import settings
from knowledge.models import Question, Response
import logging
from knowledge.models import Category
# Get an instance of a logger
logger = logging.getLogger(__name__)

OPTIONAL_FIELDS = ['alert', 'phone_number']


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
            selected_fields = ['name', 'email', 'title', 'body']
    else:
        selected_fields = ['user', 'title', 'body', 'status']

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
        phone_number = forms.CharField(label=_('Phone number'), required=False)
        captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'ru'})

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
            selected_fields = ['name', 'email', 'title', 'body', 'categories', 'phone_number']
    else:
        selected_fields = ['user', 'title', 'body', 'status', 'categories', 'phone_number']

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
        phone_number = forms.CharField(label=_('Phone number'), required=False)
        #captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'ru'})
        #categories = forms.MultipleChoiceField(choices=CAT_CHOICES, required=True)
        #categories = forms.ChoiceField(choices=Category.objects.values_list('id','title'), required=True)
        #categories = forms.MultipleHiddenInput(choices=Category.objects.all())
        #categories = forms.HiddenInput(initial=2)

        def clean_user(self):
            return user

        class Meta:
            model = Question
            fields = selected_fields

    return _QuestionAskForm(*args, **kwargs)


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
        phone_number = forms.CharField(label=_('Phone number'), required=False)
        captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'ru'})

        def clean_user(self):
            return user

        def clean_question(self):
            return question

        class Meta:
            model = Response
            fields = selected_fields

    return _ResponseForm(*args, **kwargs)
