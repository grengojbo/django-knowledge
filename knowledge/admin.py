# -*- mode: python; coding: utf-8; -*-
from django.contrib import admin

from knowledge.models import Question, Response, Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Category._meta.fields]
    prepopulated_fields = {'slug': ('title', )}
admin.site.register(Category, CategoryAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Question._meta.fields]
    list_select_related = True
    #inlines = [AttachmentInline]
    raw_id_fields = ['user']
admin.site.register(Question, QuestionAdmin)


class ResponseAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Response._meta.fields]
    list_select_related = True
    raw_id_fields = ['user', 'question']
admin.site.register(Response, ResponseAdmin)


# class AttachmentInline(admin.StackedInline):
#     model = Attachment