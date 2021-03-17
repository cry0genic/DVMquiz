from .models import Member, Question, Answer, Response, MemberQuestion
from .forms import AddQuestion

from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import os
import re
import datetime
import random


def generate_keys():
    key_list = []

    y = random.randint(0, 11)
    while True:
        z = random.randint(0, 11)
        if z == y:
            continue
        else:
            break
    key_list = [y, z]
    return key_list


def leaderboard(request):
    return render(request, "gamblingMaths/leaderboard.html")


def instructions(request):
    return render(request, "gamblingMaths/instruction.html")


@login_required(login_url="/sign_in")
def index(request):
    current_member = Member.objects.get(user=request.user)
    if current_member.submitted:
        return redirect("/leaderboard")
    else:
        return render(request, "gamblingMaths/index.html")


def sign_in(request):
    if request.user.is_anonymous:
        return render(request, "gamblingMaths/sign_in.html")
    else:
        return redirect("/")


# ------------------------------------------------------------------------------------------------------
# This view will create a member object assosciated with the user object on log in but only if it does not exist.
def create_member(request):
    user = request.user
    name = user.first_name + " " + user.last_name
    if Member.objects.filter(user=user).exists():
        return redirect(
            "/instructions"
        )  # Redirect to wherever you want the user to go to after logging in.
    else:
        name = user.first_name + " " + user.last_name
        new_member = Member(user=user, name=name)
        new_member.save()
        generate_questions(request)  # generate questions
        return render(
            request, "gamblingMaths/add_members.html"
        )  # Redirect to wherever you want the user to go to after logging in.


def generate_questions(request):
    current_member = Member.objects.get(user=request.user)
    if current_member.questions_generated:
        pass
    else:
        for x in range(0, 5):
            questions = Question.objects.filter(pool=x + 1)
            print(questions)
            rand_list = generate_keys()
            print(rand_list)
            # Generate a list of two *different* random integers between 1 and 19, both inclusive.
            for y in range(2):
                question = MemberQuestion.objects.create(
                    index=y + x * 2,
                    member=current_member,
                    question=questions[rand_list[y]],
                    pool=x + 1,
                )
            current_member.questions_generated = True
            current_member.save()


@csrf_exempt
def add_team_member(request):
    user = request.user
    if request.method == "POST":
        current_member = Member.objects.get(user=user)
        team_member_email = request.POST.get("team_member_email")
        team_member_name = request.POST.get("team_member_name")

        # Only set the new values if they don't already exist.
        for member in Member.objects.all():
            if (
                member.user.email == team_member_email
                or member.team_member_email == team_member_email
            ):
                return JsonResponse(
                    {"message": "Email address already registered."}, status=204
                )

        current_member.team_member_email = team_member_email
        current_member.team_member_name = team_member_name
        current_member.name = current_member.name + " & " + team_member_name
        # Change the name of the member to include both members' names.

        current_member.save()

        return JsonResponse({"message": "Email registered"}, status=200)


@login_required
def submit_if_eliminated(request):
    current_member = Member.objects.get(user=request.user)
    if current_member.score == 0:
        current_member.is_eliminated = True
    else:
        current_member.is_eliminated = False

    if current_member.is_eliminated:
        
        return redirect("/submitquiz")
    else:
        pass


@login_required(login_url="/sign_in")
def sign_out(request):
    submit(request)
    logout(request)
    return redirect("/sign_in")

@csrf_exempt
@login_required
def set_uncertainty(request):
    range_factor = 5
    #checks for max and min of pass_uncertainty
    uncertainty = int(request.POST.get("uncertainty"))
    lower = uncertainty - range_factor
    upper = uncertainty + range_factor + 1

    final_uncertainty = random.randint(lower, upper)

    current_member = Member.objects.get(user=request.user)
    current_member.uncertainty = final_uncertainty
    current_member.save()
    return JsonResponse({"message":"Updated Uncertainty."})




# --------------------------------------------------------------------------------------------------------------------------------------------------------------


@csrf_exempt
def add_to_review(request):
    current_member = Member.objects.get(user=request.user)
    if request.method == "POST":
        queskey = request.POST.get("queskey")
        question = Question.objects.get(questionkey=queskey)

        if current_member.questions_attempted.filter(questionkey=queskey).exists():
            current_member.questions_attempted.remove(question)
        if current_member.not_attempted.filter(questionkey=queskey).exists():
            current_member.not_attempted.remove(question)
        if current_member.ar_questions.filter(questionkey=queskey).exists():
            current_member.ar_questions.remove(question)

        current_member.marked_for_review.add(question)

        return HttpResponse(
            "Question marked for review"
        )  # This needs to be changed later
    else:
        q = current_member.marked_for_review.all()
        atrlist = []
        for question in q:
            atrlist.append(question.questionkey)
        data = {"atrlist": atrlist}
        return JsonResponse(data)


@csrf_exempt
def add_to_not_attempted(request):
    current_member = Member.objects.get(user=request.user)
    if request.method == "POST":
        queskey = request.POST.get("queskey")
        question = Question.objects.get(questionkey=queskey)
        # To make sure that a question does not appear in attempted and not attempted both.
        if current_member.questions_attempted.filter(questionkey=queskey).exists():
            current_member.questions_attempted.remove(question)
        if current_member.marked_for_review.filter(questionkey=queskey).exists():
            current_member.marked_for_review.remove(question)
        if current_member.ar_questions.filter(questionkey=queskey).exists():
            current_member.ar_questions.remove(question)

        current_member.not_attempted.add(question)

        return HttpResponse(
            "Question added to not attempted"
        )  # This needs to be changed later
    else:
        q = current_member.not_attempted.all()
        atnalist = []
        for question in q:
            atnalist.append(question.questionkey)
        data = {"atnalist": atnalist}
        return JsonResponse(data)


@csrf_exempt
def add_to_attempted(request):
    current_member = Member.objects.get(user=request.user)
    if request.method == "POST":
        queskey = request.POST.get("queskey")
        question = Question.objects.get(questionkey=queskey)
        # To make sure that a question does not appear in attempted and not attempted both.
        if current_member.marked_for_review.filter(questionkey=queskey).exists():
            current_member.marked_for_review.remove(question)
        if current_member.not_attempted.filter(questionkey=queskey).exists():
            current_member.not_attempted.remove(question)
        if current_member.ar_questions.filter(questionkey=queskey).exists():
            current_member.ar_questions.remove(question)

        current_member.questions_attempted.add(question)

        return HttpResponse(
            "Question added to attempted"
        )  # This needs to be changed later
    else:
        q = current_member.questions_attempted.all()
        atalist = []
        for question in q:
            atalist.append(question.questionkey)
        data = {"atalist": atalist}
        return JsonResponse(data)


@csrf_exempt
def add_to_ar(request):
    current_member = Member.objects.get(user=request.user)
    if request.method == "POST":
        queskey = request.POST.get("queskey")
        question = Question.objects.get(questionkey=queskey)
        # To make sure that a question does not appear in attempted and not attempted both.
        if current_member.marked_for_review.filter(questionkey=queskey).exists():
            current_member.marked_for_review.remove(question)
        if current_member.not_attempted.filter(questionkey=queskey).exists():
            current_member.not_attempted.remove(question)
        if current_member.questions_attempted.filter(questionkey=queskey).exists():
            current_member.questions_attempted.remove(question)

        current_member.ar_questions.add(question)

        return HttpResponse(
            "Question added to attempted"
        )  # This needs to be changed later
    else:
        q = current_member.ar_questions.all()
        arlist = []
        for question in q:
            arlist.append(question.questionkey)
        data = {"arlist": arlist}
        return JsonResponse(data)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------


@csrf_exempt
def get_no_of_questions(request):
    no_of_questions = Question.objects.count()

    data = {"no_of_questions": no_of_questions}
    return JsonResponse(data)


@csrf_exempt
def get_question_status(request):
    current_member = Member.objects.get(user=request.user)
    atrlist = []
    atnalist = []
    atalist = []
    arlist = []

    for question in current_member.marked_for_review.all():  # Add to review
        atrlist.append(question.questionkey)
    for question in current_member.not_attempted.all():  # Add to not_attempted
        atnalist.append(question.questionkey)
    for question in current_member.questions_attempted.all():  # Add to attempted
        atalist.append(question.questionkey)
    for question in current_member.ar_questions.all():  # Add to attempted and reviewed
        arlist.append(question.questionkey)
    x = int(Question.objects.count())

    data = {
        "reviewQues": atrlist,
        "attemptedQues": atalist,
        "unattemptedQues": atnalist,
        "reviewAttemptedQues": arlist,
        "numOfQuestions": x,
    }
    return JsonResponse(data)


@csrf_exempt
def delete_response(request):
    current_member = Member.objects.get(user=request.user)
    if request.method == "POST":
        queskey = request.POST.get("queskey")
        question = Question.objects.get(questionkey=queskey)
        try:
            response = Response.objects.filter(question=question, member=current_member)
            response.delete()
        except:
            pass


@csrf_exempt
# @login_required(login_url='/sign_in')
def store_response(request):
    current_member = Member.objects.get(user=request.user)
    if request.method == "POST":
        queskey = request.POST.get("queskey")
        question = Question.objects.get(questionkey=queskey)
        try:
            anskey = request.POST.get("anskey")
            answers = question.answers.all()
            answer = answers.get(key=anskey)
            try:
                a = Response.objects.filter(member=current_member, question=question)[0]
                a.answer_mcq = answer
                a.save()
            except:
                a = Response(
                    member=current_member, question=question, answer_mcq=answer
                )
                a.save()
        except:
            answer = request.POST.get("answer")
            try:
                a = Response.objects.filter(member=current_member, question=question)[0]
                a.answer_text = answer
                a.save()
            except:
                a = Response(
                    member=current_member, question=question, answer_text=answer
                )
                a.save()
        return HttpResponse("Answer stored")


def get_leaderboard(request):
    current_member = Member.objects.get(user=request.user)
    if current_member.submitted:
        leaderboard = Member.objects.order_by("-score")
        ranklist = []
        scorelist = []
        for member in leaderboard:
            if member.submitted:
                ranklist.append(member.name)
                scorelist.append(member.score)
        data = {"ranklist": ranklist, "scorelist": scorelist}
        return JsonResponse(data)
    else:
        return HttpResponse("IDK what to put here")


@login_required(login_url="/sign_in")
def submit(request):
    current_member = Member.objects.get(user=request.user)

    if current_member.submitted == False:
        current_member.submitted = True
        current_member.save()
        try:
            full_response = current_member.full_response.all()
            for response in full_response:
                question = response.question
                try:
                    if response.answer_mcq.is_correct:
                        current_member.score = (
                            current_member.score + question.score_increment
                        )
                        current_member.answered_correctly.add(response.question)
                    else:
                        current_member.score = (
                            current_member.score - question.score_decrement
                        )
                        current_member.answered_incorrectly.add(response.question)
                except:
                    if response.answer_text == question.answer:
                        current_member.score = (
                            current_member.score + question.score_increment
                        )
                        current_member.answered_correctly.add(response.question)
                    else:
                        current_member.score = (
                            current_member.score - question.score_decrement
                        )
                        current_member.answered_incorrectly.add(response.question)
                current_member.save()
            print('this function 2') #error in this func
            return redirect("/submitquiz")
            
            
        except:
            return redirect("/leaderboard")
    else:
        return redirect("/leaderboard")


@login_required(login_url="/sign_in")
def get_result(request):
    current_member = Member.objects.get(user=request.user)
    if current_member.submitted:
        name = current_member.name
        correct = current_member.answered_correctly.all().count()
        incorrect = current_member.answered_incorrectly.all().count()
        unattempted = Question.objects.all().count() - correct - incorrect
        score = current_member.score

        leaderboard = Member.objects.filter(submitted=True).order_by("-score")
        rank = 1
        for member in leaderboard:
            if not member == current_member:
                rank = rank + 1
            else:
                break

        data = {
            "name": name,
            "correct": correct,
            "incorrect": incorrect,
            "unattempted": unattempted,
            "rank": rank,
            "score": score,
        }
        return JsonResponse(data)
    else:
        return HttpResponse("You think you're smart?")


@login_required(login_url="/sign_in")
def get_score(request):
    current_member = Member.objects.get(user=request.user)
    if current_member.submitted:
        data = {"score": current_member.score}
        return JsonResponse(data)
    else:
        return HttpResponse("The user needs to submit first")


# @login_required(login_url='/sign_in')
def get_question(request, queskey):
    current_member = Member.objects.get(user=request.user)
    current_question = Question.objects.get(questionkey=queskey)
    marked_key = 100
    entered_answer = ""
    try:
        response = Response.objects.filter(
            member=current_member, question=current_question
        )[0]
        marked_key = response.answer_mcq.key
    except:
        pass

    try:
        response = Response.objects.filter(
            member=current_member, question=current_question
        )[0]
        entered_answer = response.answer_text
    except:
        pass

    if current_question.is_image:
        base = settings.MEDIA_ROOT
        media = os.path.abspath(os.path.join(base, os.pardir))
        image_url = current_question.image.url
    else:
        image_url = 0

    if current_question.is_mcq == True:
        answerlist = []
        keylist = []
        for answer in current_question.answers.all():
            answerlist.append(answer.content)
            keylist.append(answer.key)
        data = {
            "question": current_question.content,
            "answers": answerlist,
            "keys": keylist,
            "mcq_flag": True,
            "image_flag": current_question.is_image,
            "marked_answer": marked_key,
            "image_url": image_url,
        }
        return JsonResponse(data)
    else:
        data = {
            "question": current_question.content,
            "mcq_flag": False,
            "entered_answer": entered_answer,
        }
        return JsonResponse(data)


@csrf_exempt
def get_time_remaining(request):
    current_member = Member.objects.get(user=request.user)
    if request.method == "POST":

        if current_member.has_started:

            return HttpResponse(status=204)

        else:
            current_member.start_time = timezone.now()
            current_member.has_started = True
            current_member.save()
            return HttpResponse(status=204)

    else:

        start_time = current_member.start_time
        quiz_time = datetime.timedelta(minutes=30)
        end_time = start_time + quiz_time
        time_remaining = end_time - datetime.datetime.now(
            timezone.utc
        )  # A datetime.timedelta object

        if time_remaining.seconds > 1800 or time_remaining.seconds < 0:

            data = {"message": "Time is out of range"}
            return JsonResponse(data)

        data = {
            "time_remaining": time_remaining.seconds,
        }

        return JsonResponse(data)


@csrf_exempt
def get_ques_attempted(request):
    current_member = Member.objects.get(user=request.user)
    ques_remaining = MemberQuestion.objects.filter(member = current_member).count()
    ques_attempted = 10 - ques_remaining

    data = {
        "ques_attempted":ques_attempted,
    }

    return JsonResponse(data)


@staff_member_required
def add_question(request):
    if request.method == "POST":
        form = AddQuestion(request.POST)
        if form.is_valid():
            ques_content = form.cleaned_data.get("question_content")
            key = form.cleaned_data.get("question_key")
            question = Question(questionkey=key, content=ques_content, is_mcq=True)
            question.save()
            question = Question.objects.get(questionkey=key)

            for i in range(4):
                content = form.cleaned_data.get("option_" + str(i + 1))
                answer = Answer(parent_question=question, content=content, key=i + 1)
                answer.save()

            true_key = form.cleaned_data.get("true_option")
            answer = question.answers.get(key=true_key)
            answer.is_correct = True
            answer.save()
            return redirect("/add_question")
        else:
            return HttpResponse("Please check the data you have entered")
    else:
        form = AddQuestion()
        set_key = len(Question.objects.all())
        return render(
            request,
            "gamblingMaths/add_question.html",
            {"form": form, "newkey": set_key},
        )
