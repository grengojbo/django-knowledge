# -*- mode: python; coding: utf-8; -*-
from knowledge.utils import get_module
from knowledge import settings
import logging
#from models import Category


logger = logging.getLogger(__name__)

def send_alerts(target_dict, response=None, question=None, **kwargs):
    """
    This can be overridden via KNOWLEDGE_ALERTS_FUNCTION_PATH.
    """
    from django.contrib.auth.models import User
    from django.template.loader import render_to_string
    from django.contrib.sites.models import Site
    from django.core.mail import EmailMultiAlternatives

    site = Site.objects.get_current()

    for email, name in target_dict.items():
        if isinstance(name, User):
            name = u'{0} {1}'.format(name.first_name, name.last_name)
        else:
            name = name[0]

        context = {
            'name': name,
            'email': email,
            'response': response,
            'question': question,
            'site': site
        }
        logger.debug("Send Message to: {0}".format(email))

        subject = render_to_string('django_knowledge/emails/subject.txt', context)

        message = render_to_string('django_knowledge/emails/message.txt', context)

        message_html = render_to_string('django_knowledge/emails/message.html', context)

        subject = u' '.join(line.strip() for line in subject.splitlines()).strip()
        msg = EmailMultiAlternatives(subject, message, to=[email])
        msg.attach_alternative(message_html, 'text/html')
        msg.send()


def knowledge_post_save(sender, instance, created, **kwargs):
    """
    Gathers all the responses for the sender's parent question
    and shuttles them to the predefined module.
    """
    from knowledge.models import Question, Response, Category
    from django.contrib.auth.models import User

    func = get_module(settings.ALERTS_FUNCTION_PATH)
    logger.debug('SEND knowledge_post_save')
    if settings.ALERTS and created:
        # pull together the out_dict:
        #    {'e@ma.il': ('first last', 'e@ma.il') or <User>}
        if isinstance(instance, Response):
            instances = list(instance.question.get_responses())
            instances += [instance.question]

            # dedupe people who want alerts thanks to dict keys...
            out_dict = dict([[i.get_email(), i.get_user_or_pair()]
                            for i in instances if i.alert])

        elif isinstance(instance, Question):
            # TODO: отправка почты всем is_staff переделать на категории
            #staffers = User.objects.filter(is_staff=True)
            #out_dict = dict([[user.email, user] for user in staffers if user.has_perm('change_question')])
            try:
                cat_id = instance.categories.pk
            except:
                cat_id = 1
            logger.debug('>>> categories.id={0}'.format(cat_id))
            staffers = Category.objects.select_related().get(pk=cat_id)
            #staffers =Category.objects.select_related().get(Question.categories)
            out_dict = dict([[user['email'], user['username']] for user in staffers.user.values()])

        # remove the creator...
        if instance.get_email() in out_dict.keys():
            del out_dict[instance.get_email()]

        func(
            target_dict=out_dict,
            response=instance if isinstance(instance, Response) else None,
            question=instance if isinstance(instance, Question) else None
        )
