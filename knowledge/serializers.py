# -*- mode: python; coding: utf-8; -*-
__author__ = 'jbo'

from rest_framework import serializers
from .models import Question

class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('name', 'phone_number', 'email', 'title', 'body')