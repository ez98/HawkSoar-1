from django.forms import formset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from db_connect.filters import *
from db_connect.forms import *
import datetime
from time import timezone

#HELPER FUNCTIONS
def get_user(user):
    if user.user_type == 'student':
        return Student.objects.get(user_id=user.id)
    if user.user_type == 'mentor':
        return Mentor.objects.get(user_id=user.id)
    if user.user_type == 'tutor':
        return Tutor.objects.get(user_id=user.id)
    
def get_events(request):
    user = get_user(request.user)
    has_events = list(Has_Events.objects.filter(id=user.id)) #this returns a list of Has_Events objects that match the users id
    print(has_events)
    events = []
    for e in has_events: #for each Has_Event object in 'has_events' we get the Event object from the Events table in our db
        events.append(Events.objects.get(pk=e.event_id.pk))
    return events
#HELPER FUNCTIONS (END)

#SIGN UP AND LOGIN/LOGOUT VIEWS INCLUDING ROLE MANAGER (DIRECTS USERS TO THEIR DASHBOARD)
def user_signup(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            userType = form.cleaned_data['user_type']
            if userType not in ['student', 'tutor', 'mentor']:
                return HttpResponseBadRequest("Invalid user type")
            
            name = form.cleaned_data['first_name'] + ' ' + form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            cwid = request.POST.get('cwid')
            major = request.POST.get('major')
            user = form.save() #user instance is posted to db auth_user
            if userType == 'student':
                student = Student.objects.create(user=user, A_number=cwid, Student_Name=name, Student_email=email, Major=major)
                student.save()
                return redirect('course_quantity', cwid)
            if userType == 'tutor':
                tutor = Tutor.objects.create(user=user, Tid=cwid, email=email)
                tutor.save()
                return redirect('tutor_course', cwid)
            if userType == 'mentor':
                mentor = Mentor.objects.create(user=user, Mid=cwid, name=name, email=email)
                mentor.save()
            
            return redirect('login_view')
    else:
        form = UserSignUpForm()
    return render(request, 'user_signup.html', {'form': form})    

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email') #get the email from the login html form
        password = request.POST.get('password') #get the pw from the login html form
        user = authenticate(request, email=email, password=password) #authenticate the user by checking the credentials in the user_register table
        if user is not None:
            login(request, user) #if they exists create a new session and log them in
            return redirect('role_manager') #redirect them to the events they've signed up for
        else:
            messages.error(request, 'Invalid email or password. Please Try Again')
    form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login_view')

@login_required
def role_manager(request):
    user_role = request.user.user_type
    user = get_user(request.user)
    if user_role == 'student':
        return redirect('student', user_id=user.id)
    elif user_role == 'tutor':
        return redirect('tutor', user_id=user.id)
    elif user_role == 'mentor':
        return redirect('mentor', user_id=user.id)
    else:
        return HttpResponseBadRequest("Invalid user type")
#END

#VIEWS THAT RENDER THE CORRESPONDING DASHBOARD PAGES FOR EACH USER
@login_required
def student(request, user_id):
    user = get_user(request.user)
    events = get_events(request)
    return render(request, 'student_home.html', {'user': user, 'events': events})

@login_required
def tutor(request, user_id):
    cids = []
    for object in TutorsCourse.objects.filter(Tid=user_id):
        cids.append(object.course_id)
    students = []
    for cid in cids:
        course = Course_Registered.objects.get(Course_id=cid)
        if course.Course_id == cid:
            students.append([course.A_number.Student_Name, course.A_number.A_number, course.Course_Name])
    Tid = Tutor.objects.get(id=user_id).Tid
    return render(request, 'tutor_home.html', {'user_id': user_id, 'students': students, 'Tid':Tid})

@login_required
def mentor(request, user_id):
    user = get_user(request.user)
    meeting_objects = MentorMeeting.objects.filter(Mid=user_id)
    meetings = []

    for meeting in meeting_objects:
        student_name = meeting.A_number.Student_Name
        date = meeting.mDate.date()
        time = meeting.mDate.time()
        dt = str(date) + ' ' + str(time)
        meetings.append([meeting.mName, dt, student_name])
    print(meetings)
    return render(request, 'mentor_home.html', {'user_id': user_id, 'meetings':meetings})
#END


#####################################
#VIEWS FOR ANY USER TO USE (excepts students can't use event_create)
#####################################
@login_required
def room(request, room_name, user_id):
    return render(request, 'chatroom.html', {
        'room_name': room_name,
        'user_id':user_id
    })

@login_required
def event_create(request, user_id):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            if request.user.user_type == 'tutor':
                return redirect('tutor')
            if request.user.user_type == 'mentor':
                return redirect('mentor')
    else:
        form = EventForm()
    return render(request, 'event_create.html', {'user_id':user_id, 'form': form})

@login_required
def collaboration_portal(request, user_id):
    #this would allow users to look up other users in the database and connect with them
    return HttpResponse("Work in progess.")
#####################################
#VIEWS FOR ANY USER (END)
#####################################


#STUDENT VIEWS


@login_required
def event_signup(request, user_id):
    events = Events.objects.all()
    user = get_user(request.user)
    print("GOT USER PROFILE,", user)
    if request.method == 'POST':
        event_pk = request.POST.get('event')
        event = Events.objects.get(pk=event_pk)
        has_events = Has_Events(A_number=user, event_id=event, event_name=event, event_date=event)
        has_events.save()
        return redirect('student', user_id)
    return render(request, 'event_signup.html', {'events': events})

def course_quantity(request, A_number):
    if request.method == 'POST':
        num_courses = int(request.POST.get('num_courses'))
        return redirect('register_courses', A_number, num_courses)
    return render(request, 'course_quantity.html')

#User signs up -> User selects number of course they're taking in course_quantity() -> register_courses()
def register_courses(request, A_number, extra):
    CourseFormSet = formset_factory(CoursesForm, extra=extra)
    if request.method == 'POST':
        formset = CourseFormSet(request.POST)
        if formset.is_valid():
            student = Student.objects.get(A_number=A_number)
            for form in formset:
                course_id = form.cleaned_data.get('Course_id')
                course_name = form.cleaned_data.get('Course_Name')
                course = Course_Registered.objects.create(A_number=student, Course_id=course_id, Course_Name=course_name)
                course.save()
            return redirect('login_view')
    else:
        formset = CourseFormSet()
    return render(request, 'course_register.html', {'formset': formset, 'A_number': A_number})

@login_required
@require_GET
def my_assignments(request, user_id):
    try:
      current_time = timezone.now()
      assignments = Assignments.objects.filter(student=request.user_id,due_date__gte=current_time).order_by('due_date')
      context = {
        'assignments': assignments,}
    except:
        return HttpResponse("Oops, something went wrong! Please try again later.")
    return render(request, 'my_assignments.html', context)

@login_required
@require_GET
def my_schedule(request, user_id):
    try:
       current_time = timezone.now()
       events = Events.objects.filter(student=request.user,start_time__gte=current_time).order_by('start_time')
       class_schedule = ClassSchedule.objects.filter(student=request.user,
        start_date__lte=current_time.date(),
        end_date__gte=current_time.date(),).order_by('day_of_week', 'start_time')
       context = {
        'events': events,
        'class_schedule': class_schedule,}
       
    except:
        return HttpResponse("Oops, something went wrong! Please try again later.")

    return render(request, 'my_schedule.html', context)

@login_required
@require_GET
def performance_report(request, user_id):
    try:
       student = Student.objects.get(A_number=user_id)
       courses = Course_Registered.objects.filter(A_number=student).distinct()
       performance_data = []
       for course in courses:
            enrollments = enrollments.objects.filter(
            student=request.user,
            course=course,
            grade__isnull=False)
            grades = [enrollment.grade for enrollment in enrollments]
            
            if grades:
               gpa = sum(grades) / len(grades)
               letter_grade = get_letter_grade(gpa)
            else:
               gpa = None
               letter_grade = None
               feedback = Feedback.objects.filter(student=request.user,course=course).first()
               performance_data.append({
               'course': course,
               'gpa': gpa,
               'letter_grade': letter_grade,
               'feedback': feedback,})
            context = {'performance_data': performance_data,}
    except:
        return HttpResponse("Oops, something went wrong! Please try again later.")

    return render(request, 'performance_report.html', context)



def get_letter_grade(gpa):
    if gpa >= 4.0:
        return 'A'
    elif gpa >= 3.7:
        return 'A-'
    elif gpa >= 3.3:
        return 'B+'
    elif gpa >= 3.0:
        return 'B'
    elif gpa >= 2.7:
        return 'B-'
    elif gpa >= 2.3:
        return 'C+'
    elif gpa >= 2.0:
        return 'C'
    elif gpa >= 1.7:
        return 'C-'
    elif gpa >= 1.3:
        return 'D+'
    elif gpa >= 1.0:
        return 'D'
    else:
        return 'F'
#STUDENT VIEWS (END)

#TUTOR VIEWS
def tutor_course(request, Tid):
    if request.method == 'POST':
        tutor = Tutor.objects.get(Tid=Tid)
        course_ids_list = request.POST.getlist('courses[]')
        for course_string in course_ids_list:
            cin, cname = course_string.split('-') #get id and name, by splitting '-' between the course_id variable
            tutor_course = TutorsCourse.objects.create(Tid=tutor, course_id=cin, cname=cname)
            tutor_course.save()
        return redirect('login_view')
    else:
        courses = Course_Registered.objects.all()
        myFilter = CourseFilter(request.GET, queryset=courses)
        courses = myFilter.qs
        context = { 'courses':courses, 'myFilter':myFilter }
        return render(request, 'tutor_course.html', context)

@login_required
def assign_group(request):
    #use django filter to let user filter students by course 
    #User can select a course they tutor from a dropdown list 
    #Once selected, use filter to get students in that course
    #Let user select students to assign to a group
    #Fill out fields GID, Group Name, CID, A_number
    #Have to create n instances for n students for the Group model
    pass
@login_required
def assignment_manager(request, user_id):
    return HttpResponse("Work in progess.")
@login_required
def performance_manager(request, user_id):
    return HttpResponse("Work in progess.")
@login_required
def submit_feedback(request):
    return HttpResponse("Work in progess.")
#TUTOR VIEWS (END)

#MENTOR VIEWS
@login_required
def meeting_scheduler(request, user_id):
    if request.method == 'POST':
        mentor = Mentor.objects.get(id=user_id)
        mName = request.POST.get('meeting-name')
        student_id = request.POST.get('selected-student')
        student = Student.objects.get(id=student_id)
        _date = request.POST.get('meeting-date')
        _time = request.POST.get('meeting-time')
        date = datetime.datetime.strptime(_date, '%Y-%m-%d').date()
        time = datetime.datetime.strptime(_time, '%H:%M').time()
        dt = datetime.datetime.combine(date, time)
        mentor_meeting = MentorMeeting.objects.create(Mid=mentor, A_number=student, mName=mName, mDate=dt)
        mentor_meeting.save()
        return redirect('mentor', user_id)
    else:
        students = Student.objects.all()
        myFilter = StudentFilter(request.GET, queryset=students)
        students = myFilter.qs
        context = { 'students':students, 'myFilter':myFilter, 'user_id':user_id }
        return render(request, 'meeting_scheduler.html', context)
#MENTOR VIEWS (END)


