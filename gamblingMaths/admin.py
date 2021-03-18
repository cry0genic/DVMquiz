from django.contrib import admin
from .models import Member, Question, Answer, Response, MemberQuestion
from django.contrib.auth.models import Group

class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ['questionkey', 'content', 'pool', 'image', ('is_image', 'is_mcq'), 'answer']
    inlines = [AnswerInline]

admin.autodiscover()
admin.site.register(Member)
#admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Response)
admin.site.register(MemberQuestion)
