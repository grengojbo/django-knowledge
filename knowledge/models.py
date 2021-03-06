# -*- mode: python; coding: utf-8; -*-
from knowledge import settings
from django.contrib.auth.models import User

import django
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings as django_settings

from knowledge.managers import QuestionManager, ResponseManager
from knowledge.signals import knowledge_post_save

STATUSES = (
    ('public', _('Public')),
    ('private', _('Private')),
    ('internal', _('Internal')),
)


STATUSES_EXTENDED = STATUSES + (
    ('inherit', _('Inherit')),
)


class Category(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    lastchanged = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    user = models.ManyToManyField(User, blank=True, null=True)
    tpl_subject = models.CharField(verbose_name=_(u'Шаблон ззаголовка'), max_length=255, default='subject.txt',
                                   help_text=_(u'папка с шаблон templates/django_knowledge/emails/'))
    tpl_message = models.CharField(verbose_name=_(u'Шаблон повідомлення'), max_length=255, default='message.txt',
                                   help_text=_(u'папка с шаблон templates/django_knowledge/emails/'))
    tpl_message_html = models.CharField(verbose_name=_(u'Шаблон повідомлення HTML'), max_length=255,
                                        default='message.html',
                                        help_text=_(u'папка с шаблон templates/django_knowledge/emails/'))

    def __unicode__(self):
        return u"{0}".format(self.title)

    class Meta:
        ordering = ['title']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class KnowledgeBase(models.Model):
    """
    The base class for Knowledge models.
    """
    is_question, is_response = False, False

    added = models.DateTimeField(auto_now_add=True)
    lastchanged = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('auth.User', blank=True, null=True, db_index=True)
    alert = models.BooleanField(default=settings.ALERTS, verbose_name=_('Alert'), help_text=_('Check this if you want to be alerted when a new response is added.'))
    # for anonymous posting, if permitted
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter your first and last name.'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'), help_text=_('Enter a valid email address.'))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.user and self.name and self.email and not self.id:
            # first time because no id
            self.public(save=False)

        if settings.AUTO_PUBLICIZE and not self.id:
            self.public(save=False)

        super(KnowledgeBase, self).save(*args, **kwargs)

    #########################
    #### GENERIC GETTERS ####
    #########################

    def get_name(self):
        """
        Get local name, then self.user's first/last, and finally
        their username if all else fails.
        """
        name = (self.name or u'{0} {1}'.format(self.user.first_name, self.user.last_name))
        return name.strip() or self.user.username

    get_email = lambda s: s.email or (s.user and s.user.email)
    get_pair = lambda s: (s.get_name(), s.get_email())
    get_user_or_pair = lambda s: s.user or s.get_pair()

    ########################
    #### STATUS METHODS ####
    ########################

    def can_view(self, user):
        """
        Returns a boolean dictating if a User like instance can
        view the current Model instance.
        """

        if self.status == 'inherit' and self.is_response:
            return self.question.can_view(user)

        if self.status == 'internal' and user.is_staff:
            return True

        if self.status == 'private':
            if self.user == user or user.is_staff:
                return True
            if self.is_response and self.question.user == user:
                return True

        if self.status == 'public':
            return True

        return False

    def switch(self, status, save=True):
        self.status = status
        if save:
            self.save()
    switch.alters_data = True

    def public(self, save=True):
        self.switch('public', save)
    public.alters_data = True

    def private(self, save=True):
        self.switch('private', save)
    private.alters_data = True

    def inherit(self, save=True):
        self.switch('inherit', save)
    inherit.alters_data = True

    def internal(self, save=True):
        self.switch('internal', save)
    internal.alters_data = True


class Question(KnowledgeBase):
    is_question = True
    _requesting_user = None

    title = models.CharField(max_length=255, verbose_name=_('Question'),
                             help_text=_('Enter your question or suggestion.'))
    body = models.TextField(blank=True, null=True, verbose_name=_('Description'),
                            help_text=_('Please offer details. Markdown enabled.'))
    status = models.CharField(verbose_name=_('Status'), max_length=32, choices=STATUSES, default='private',
                              db_index=True)
    locked = models.BooleanField(default=False)
    #categories = models.ManyToManyField('knowledge.Category', blank=True, null=True)
    categories = models.ForeignKey('knowledge.Category', verbose_name=_(u'Category'), blank=True, null=True)
    phone_number = models.CharField(_('Phone number'), blank=True, null=True, max_length=15)
    company = models.CharField(max_length=255, verbose_name=_(u'Kомпанія'), help_text=_(u'Назва вашої компанії.'),
                               blank=True, null=True)
    activities = models.CharField(max_length=255, verbose_name=_(u'Види діяльності'),
                                  help_text=_(u'Види діяльності на орендованій площі.'), blank=True, null=True)
    trading = models.CharField(max_length=255, verbose_name=_(u'Товарна група'), help_text=_(u'Ваша товарна група.'),
                               blank=True, null=True)
    floor = models.CharField(max_length=255, verbose_name=_(u'Бажаний поверх'), blank=True, null=True)
    parking = models.CharField(max_length=255, verbose_name=_(u'Кількість місць'), blank=True, null=True)
    areea_leasse = models.CharField(max_length=255, verbose_name=_(u'Площа оренди'),
                                    help_text=_(u'Запланована площа оренди (м2)'), blank=True, null=True)
    date_leasse = models.CharField(max_length=255, verbose_name=_(u'Термін оренди'),
                                   help_text=_(u'На який термін плануєте оренду'), blank=True, null=True)
    trademarks = models.TextField(blank=True, null=True, verbose_name=_(u'Торгові марки'),
                                  help_text=_(u'Торгові марки, країни-виробники'))
    range_of_goods = models.TextField(blank=True, null=True, verbose_name=_(u'Асортимент'),
                                      help_text=_(u'Асортимент товарів, послуг, розваг'))
    # body = models.TextField(blank=True, null=True, verbose_name=_(u''), help_text=_(u''))
    chbox1 = models.BooleanField(default=True, verbose_name=_('Checkbox 1'))
    chbox2 = models.BooleanField(default=True, verbose_name=_('Checkbox'))

    objects = QuestionManager()

    class Meta:
        ordering = ['-added']
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __unicode__(self):
        return u'{0}'.format(self.title)

    def get_cat(self):
        return self.categories

    @models.permalink
    def get_absolute_url(self):
        from django.template.defaultfilters import slugify

        if settings.SLUG_URLS:
            return 'knowledge_thread', [self.id, slugify(self.title)]
        else:
            return 'knowledge_thread_no_slug', [self.id]

    def inherit(self):
        pass

    def internal(self):
        pass

    def lock(self, save=True):
        self.locked = not self.locked
        if save:
            self.save()
    lock.alters_data = True

    ###################
    #### RESPONSES ####
    ###################

    def get_responses(self, user=None):
        user = user or self._requesting_user
        if user:
            return [r for r in self.responses.all().select_related('user') if r.can_view(user)]
        else:
            return self.responses.all().select_related('user')

    def answered(self):
        """
        Returns a boolean indictating whether there any questions.
        """
        return bool(self.get_responses())

    def accepted(self):
        """
        Returns a boolean indictating whether there is a accepted answer
        or not.
        """
        return any([r.accepted for r in self.get_responses()])

    def clear_accepted(self):
        self.get_responses().update(accepted=False)
    clear_accepted.alters_data = True

    def accept(self, response=None):
        """
        Given a response, make that the one and only accepted answer.
        Similar to StackOverflow.
        """
        self.clear_accepted()

        if response and response.question == self:
            response.accepted = True
            response.save()
            return True
        else:
            return False
    accept.alters_data = True

    def states(self):
        """
        Handy for checking for mod bar button state.
        """
        return [self.status, 'lock' if self.locked else None]

    @property
    def url(self):
        return self.get_absolute_url()


class Response(KnowledgeBase):
    is_response = True

    question = models.ForeignKey('knowledge.Question', related_name='responses')
    body = models.TextField(blank=True, null=True, verbose_name=_('Response'),
                            help_text=_('Please enter your response. Markdown enabled.'))
    status = models.CharField(verbose_name=_('Status'), max_length=32, choices=STATUSES_EXTENDED, default='inherit',
                              db_index=True)
    accepted = models.BooleanField(default=False)

    objects = ResponseManager()

    class Meta:
        ordering = ['added']
        verbose_name = _('Response')
        verbose_name_plural = _('Responses')

    def __unicode__(self):
        return self.body[0:100] + u'...'

    def states(self):
        """
        Handy for checking for mod bar button state.
        """
        return [self.status, 'accept' if self.accepted else None]

    def accept(self):
        self.question.accept(self)
    accept.alters_data = True


def attachment_path(instance, filename):
    """
    Provide a file path that will help prevent files being overwritten, by
    putting attachments in a folder off attachments for ticket/followup_id/.
    """
    import os
    from django.conf import settings
    os.umask(0)
    #path = 'attachments/{0}/{1}'.format(instance.followup.ticket.ticket_for_url, instance.followup.id)
    path = 'attachments'
    att_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(att_path):
        os.makedirs(att_path, 0777)
    return os.path.join(path, filename)


class Attachment(models.Model):
    """
    Represents a file attached to a follow-up. This could come from an e-mail
    attachment, or it could be uploaded via the web interface.
    """

    file = models.FileField(_('File'), upload_to=attachment_path)
    filename = models.CharField(_('Filename'), max_length=100)
    mime_type = models.CharField(_('MIME Type'), max_length=255)
    size = models.IntegerField(_('Size'), help_text=_('Size of this file in bytes'))

    # def get_upload_to(self, field_attname):
    #     """ Get upload_to path specific to this item """
    #     if not self.id:
    #         return u''
    #     return u'helpdesk/attachments/%s/%s' % (
    #         self.followup.ticket.ticket_for_url,
    #         self.followup.id
    #         )

    def __unicode__(self):
        return u'%s' % self.filename

    class Meta:
        db_table = 'attachments'
        ordering = ['filename']
        verbose_name = _(u'Attachment')
        verbose_name_plural = _(u'Attachment')

# cannot attach on abstract = True... derp
models.signals.post_save.connect(knowledge_post_save, sender=Question)
models.signals.post_save.connect(knowledge_post_save, sender=Response)
