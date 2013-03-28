# -*- mode: python; coding: utf-8; -*-
import settings

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import Q
from django.views import generic

from knowledge.models import Question, Response, Category
from knowledge.forms import QuestionForm, ResponseForm, QuestionAskForm
from knowledge.utils import paginate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

ALLOWED_MODS = {
    'question': [
        'private', 'public',
        'delete', 'lock',
        'clear_accepted'
    ],
    'response': [
        'internal', 'inherit',
        'private', 'public',
        'delete', 'accept'
    ]
}


def get_my_questions(request):
    logger.debug("viev get_my_questions")
    if settings.LOGIN_REQUIRED and not request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_URL + "?next=%s" % request.path)

    if request.user.is_anonymous():
        return Question.objects.none()
    return Question.objects.can_view(request.user) \
        .filter(user=request.user)


class KnowledgeBase(object):
    """ Base class for knowledge views"""

    def get_my_questions(self):
        if self.request.user.is_anonymous():
            return Question.objects.none()
        return Question.objects.can_view(self.request.user).filter(user=self.request.user)


class KnowledgeIndex(generic.ListView, KnowledgeBase):
    """ Index page for """
    template_name = 'django_knowledge/index.html'
    context_object_name = 'questions'

    def get_queryset(self, *args, **kwargs):
        return self.get_my_questions()

    def get_context_data(self, *args, **kwargs):
        context = super(KnowledgeIndex, self).get_context_data(*args, **kwargs)
        context['my_questions'] = self.get_my_questions()
        context['categories'] = Category.objects.all().cache()
        return context


class KnowledgeList(generic.ListView, KnowledgeBase):
    template_name = 'django_knowledge/list.html'
    context_object_name = 'questions'

    def get_queryset(self, *args, **kwargs):
        qs = Question.objects.can_view(self.request.user)
        search = self.request.GET.get('title', None)

        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(body__icontains=search))

        if self.kwargs.get('category_slug', None):
            category = get_object_or_404(Category,
                                         slug=self.kwargs['category_slug'])
            qs = qs.filter(categories=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super(KnowledgeList, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get('title', None)
        context['my_questions'] = self.get_my_questions()
        context['categories'] = Category.objects.all()
        context['form'] = QuestionForm(
            self.request.user, initial={'title': context['search']})
        return context


def knowledge_thread(request,
                     question_id,
                     slug=None,
                     template='django_knowledge/thread.html',
                     Form=ResponseForm):
    logger.debug("viev django_knowledge/thread.html")
    if settings.LOGIN_REQUIRED and not request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_URL + "?next=%s" % request.path)

    try:
        question = Question.objects.can_view(request.user) \
            .get(id=question_id)
    except Question.DoesNotExist:
        if Question.objects.filter(id=question_id).exists() and \
                hasattr(settings, 'LOGIN_REDIRECT_URL'):
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            raise Http404

    responses = question.get_responses(request.user)

    if request.path != question.get_absolute_url():
        return redirect(question.get_absolute_url(), permanent=True)

    if request.method == 'POST':
        form = Form(request.user, question, request.POST)
        if form and form.is_valid():
            if request.user.is_authenticated() or not form.cleaned_data['phone_number']:
                form.save()
            return redirect(question.get_absolute_url())
    else:
        form = Form(request.user, question)

    return render(request, template, {
        'request': request,
        'question': question,
        'my_questions': get_my_questions(request),
        'responses': responses,
        'allowed_mods': ALLOWED_MODS,
        'form': form,
        'categories': Category.objects.all()
    })


def knowledge_moderate(
        request,
        lookup_id,
        model,
        mod,
        allowed_mods=ALLOWED_MODS):
    """
    An easy to extend method to moderate questions
    and responses in a vaguely RESTful way.

    :param request:
    :param lookup_id:
    :param model:
    :param mod:
    :param allowed_mods:
    Usage:
        /knowledge/moderate/question/1/inherit/     -> 404
        /knowledge/moderate/question/1/public/      -> 200

        /knowledge/moderate/response/3/notreal/     -> 404
        /knowledge/moderate/response/3/inherit/     -> 200

    """
    logger.debug("viev knowledge_moderate")
    if settings.LOGIN_REQUIRED and not request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_URL + "?next=%s" % request.path)

    if request.method != 'POST':
        raise Http404

    if model == 'question':
        Model, perm = Question, 'change_question'
    elif model == 'response':
        Model, perm = Response, 'change_response'
    else:
        raise Http404

    if not request.user.has_perm(perm):
        raise Http404

    if mod not in allowed_mods[model]:
        raise Http404

    instance = get_object_or_404(
        Model.objects.can_view(request.user),
        id=lookup_id)

    func = getattr(instance, mod)
    if callable(func):
        func()

    try:
        return redirect((
            instance if instance.is_question else instance.question
        ).get_absolute_url())
    except NoReverseMatch:
        # if we delete an instance...
        return redirect(reverse('knowledge_index'))


def knowledge_ask(request,
                  template='django_knowledge/ask.html',
                  Form=QuestionForm, forms=None):
    logger.debug("knowledge_ask")
    if settings.LOGIN_REQUIRED and not request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_URL + "?next=%s" % request.path)
        # TODO: добавить при отправке сплывающая подсказка вам отправлено сообщение....
    if request.method == 'POST':
        if forms == 'QuestionAskForm':
            form = QuestionAskForm(request.user, request.POST)
        else:
            form = QuestionForm(request.user, request.POST)
        #form = Form(request.user, request.POST)
        if form and form.is_valid():
            logging.debug(form.cleaned_data)
            if request.user.is_authenticated():
                logger.debug("FORM SEND is_authenticated")
                question = form.save()
                return redirect(question.get_absolute_url())
            else:
                logger.debug("FORM NO SEND is_anonymous")
                question = form.save()
                return redirect(settings.KN_REDIRECT_PATH)
    else:
        if forms == 'QuestionAskForm':
            form = QuestionAskForm(request.user)
        else:
            form = QuestionForm(request.user)
        #form = Form(request.user)

    return render(request, template, {
        'request': request,
        'my_questions': get_my_questions(request),
        'form': form,
        'categories': Category.objects.all()
    })
