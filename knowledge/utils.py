# -*- mode: python; coding: utf-8; -*-
from knowledge import settings
import logging
#from models import Category
#from django.conf import settings

logger = logging.getLogger(__name__)


def paginate(iterable, per_page, page_num):
    """
        recipes = Recipe.objects.all()
        paginator, recipes = paginate(recipes, 12,
            request.GET.get('page', '1'))
    """
    from django.core.paginator import Paginator, InvalidPage, EmptyPage

    paginator = Paginator(iterable, per_page)

    try:
        page = int(page_num)
    except ValueError:
        page = 1

    try:
        iterable = paginator.page(page)
    except (EmptyPage, InvalidPage):
        iterable = paginator.page(paginator.num_pages)

    return paginator, iterable


def get_module(path):
    """
    A modified duplicate from Django's built in backend
    retriever.

        slugify = get_module('django.template.defaultfilters.slugify')
    """
    from django.utils.importlib import import_module

    try:
        mod_name, func_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImportError(
            'Error importing alert function {0}: "{1}"'.format(mod_name, e))

    try:
        func = getattr(mod, func_name)
    except AttributeError:
        raise ImportError(
            ('Module "{0}" does not define a "{1}" function'
                            ).format(mod_name, func_name))

    return func


user_model_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def send_alerts(target_dict, response=None, question=None, tpl_subject='subject.txt', tpl_message='message.txt', tpl_message_html='message.html', **kwargs):
    """
    This can be overridden via KNOWLEDGE_ALERTS_FUNCTION_PATH.
    """
    from django.contrib.auth.models import User
    from django.template.loader import render_to_string
    from django.contrib.sites.models import Site
    from django.core.mail import EmailMultiAlternatives

    site = Site.objects.get_current()

    for email, name in target_dict.items():
        # if isinstance(name, User):
        #     name = u'{0} {1}'.format(name.first_name, name.last_name)
        # else:
        #     name = name[0]

        context = {
            # 'name': name,
            'email': email,
            'response': response,
            'question': question,
            'site': site
        }
        logger.debug("Send Message to: {0}".format(email))

        subject = render_to_string('django_knowledge/emails/{0}'.format(tpl_subject), context)
        subject = u' '.join(line.strip() for line in subject.splitlines()).strip()
        logger.debug(u"subject: {0}".format(subject))
        message = render_to_string('django_knowledge/emails/{0}'.format(tpl_message), context)
        logger.debug(u"message: {0}".format(message))
        message_html = render_to_string('django_knowledge/emails/{0}'.format(tpl_message_html), context)
        #logger.debug(u"message_html: {0}".format(message_html))

        msg = EmailMultiAlternatives(subject, message, to=[email])
        msg.attach_alternative(message_html, 'text/html')
        #msg.send()


def send_mail_full(mess, tpl_subject='subject.txt', tpl_message='message.txt', tpl_message_html='message.html'):
    """
    Gathers all the responses for the sender's parent question
    and shuttles them to the predefined module.
    """
    from knowledge.models import Question, Response, Category
    from django.contrib.auth.models import User

    # func = get_module(settings.ALERTS_FUNCTION_PATH)
    func = get_module('knowledge.utils.send_alerts')
    logger.debug('SEND send_mail_full categories: {0}'.format(mess.get('categories', 1)))

    staffers = Category.objects.select_related().get(pk=mess.get('categories', 1))
    out_dict = dict([[user['email'], user['username']] for user in staffers.user.values()])

    # if settings.ALERTS and created:
    #     # pull together the out_dict:
    #     #    {'e@ma.il': ('first last', 'e@ma.il') or <User>}
    #     if isinstance(instance, Response):
    #         instances = list(instance.question.get_responses())
    #         instances += [instance.question]
    #
    #         # dedupe people who want alerts thanks to dict keys...
    #         out_dict = dict([[i.get_email(), i.get_user_or_pair()]
    #                         for i in instances if i.alert])
    #
    #     elif isinstance(instance, Question):
    #         # TODO: отправка почты всем is_staff переделать на категории
    #         #staffers = User.objects.filter(is_staff=True)
    #         #out_dict = dict([[user.email, user] for user in staffers if user.has_perm('change_question')])
    #         try:
    #             cat_id = instance.categories.pk
    #         except:
    #             cat_id = 1
    #         logger.debug('>>> categories.id={0}'.format(cat_id))
    #         staffers =Category.objects.select_related().get(pk=cat_id)
    #         #staffers =Category.objects.select_related().get(Question.categories)
    #         out_dict = dict([[user['email'], user['username']] for user in staffers.user.values()])
    #
    #     # remove the creator...
    #     if instance.get_email() in out_dict.keys():
    #         del out_dict[instance.get_email()]
    #

    func(
        target_dict=out_dict,
        question=mess,
        tpl_subject=tpl_subject, tpl_message=tpl_message, tpl_message_html=tpl_message_html
    )
