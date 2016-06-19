'''
    This file contains code for running the server
'''

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, send_from_directory
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import *
from flask import session as login_session
import random
import string
import os
from math import floor
from OpenSSL import SSL

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__, static_url_path="/static")

HOST = '0.0.0.0'
PORT = 80

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Education"


# Connect to Database and create database session
engine = create_engine('sqlite:///' + DATABASE_NAME)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.teardown_request
def teardown_request(exception=None):
    '''
        Runs at the end of each request,
        regardless of whether an exception was raised
    '''
    if exception:
        session.rollback()

@app.errorhandler(500)
def internal_server_error(exception):
    flash("Something went wrong! We are sorry.")
    return redirect(url_for("showHomepage"))

@app.route("/static/<path:path>")
def sendStaticFile(path):
    return send_from_directory("static", path)

@app.route('/')
@app.route('/index.html')
def showHomepage():
    enrolled_majors = getEnrolledMajors()
    enrolled_courses = getEnrolledCourses()
    unfinished_tasks = getTopUnfinishedTasks()
    courses = []
    for course in enrolled_courses:
        progress = courseProgress(course.course_id)
        if progress < 100:
            course.progress = progress
            courses.append(course)
    return render_template('index.html',
        login_session=login_session,
        enrolled_majors=enrolled_majors,
        enrolled_courses=courses,
        unfinished_tasks=unfinished_tasks)

@app.route("/donate.html")
def showDonationPage():
    return render_template("donation.html",
        login_session=login_session)

@app.route('/exams/new', methods=['POST'])
def newExam():
    if not isAdmin():
        return
    if request.method == 'POST':
        newExam = Exam(exam_title=request.form["title"])
        session.add(newExam)
        flash("New exam %s successfully created" % newExam.exam_title)
        session.commit()
    return redirect(url_for("showExamsPage"))

@app.route("/examList.html")
def showExamsPage():
    exams = session.query(Exam).all()
    print exams
    return render_template("examList.html",
        exams=exams,
        login_session=login_session)

@app.route("/examBuilder.html")
def showExamBuilderPage():
    return render_template("examBuilder.html",
        login_session=login_session)

@app.route('/profile.html')
def showProfile():
    enrolled_majors = getEnrolledMajors()
    enrolled_courses = getEnrolledCourses()
    incomplete_courses = []
    complete_courses = []
    incomplete_majors = []
    complete_majors = []
    for course in enrolled_courses:
        progress = courseProgress(course.course_id)
        if progress < 100:
            course.progress = progress
            incomplete_courses.append(course)
        else:
            complete_courses.append(course)
    for major in enrolled_majors:
        progress = majorProgress(major.major_id)
        if progress < 100:
            incomplete_majors.append(major)
        else:
            complete_majors.append(major)
    return render_template('profile.html',
        login_session=login_session,
        incomplete_majors=incomplete_majors,
        complete_majors=complete_majors,
        complete_courses=complete_courses,
        incomplete_courses=incomplete_courses)

@app.route('/volunteer.html')
def showVolunteerPage():
    # return "The current session state is %s" % login_session['state']
    return render_template("volunteer.html", login_session=login_session)

@app.route('/admin.html')
def showAdminPage():
    if not isAdmin():
        return redirect(url_for("showHomepage"))
    return render_template('admin.html', login_session=login_session)

@app.route('/majorsPublic.html')
def showMajorsPublic():
    enrolled_majors = getEnrolledMajors()
    majors = session.query(Major).order_by(asc(Major.name))
    return render_template('majorsPublic.html', majors=majors, login_session=login_session, enrolled_majors=enrolled_majors)

@app.route('/coursesPublic.html')
def showCoursesPublic():
    enrolled_courses = getEnrolledCourses()
    courses = session.query(Course).order_by(asc(Course.name))
    return render_template('coursesPublic.html', courses=courses, login_session=login_session, enrolled_courses=enrolled_courses)

@app.route('/courses/<int:course_id>/tasks/new/', methods=['POST'])
def newTask(course_id):
    '''
        Create a new task
    '''
    if not isAdmin():
        return
    if request.method == 'POST':
        newTask = Task(
            course_id=course_id,
            name=request.form['name'],
            url=request.form['url']
        )
        session.add(newTask)
        flash('New Task %s Successfully Created' % newTask.name)
        session.commit()
    return redirect(url_for('editCourseTasks', course_id=course_id))

@app.route('/tasks/<int:task_id>/edit/', methods=['POST'])
def editTask(task_id):
    '''
        Update a task
    '''
    if not isAdmin():
        return
    editedTask = session.query(Task).filter_by(task_id=task_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedTask.name = request.form['name']
        if request.form['url']:
            editedTask.url = request.form['url']
        flash('Task Successfully Edited: %s' % editedTask.name)
        session.add(editedTask)
        session.commit()
        return redirect(url_for('editCourseTasks', course_id=editedTask.course_id))

@app.route('/courses/<int:course_id>/tasks/<int:task_id>/delete/', methods=['POST'])
def deleteTask(course_id, task_id):
    '''
        Delete a task
    '''
    if not isAdmin():
        return
    if request.method == 'POST':
        taskToDelete = session.query(Task).filter_by(task_id=task_id).one()
        session.delete(taskToDelete)
        flash('%s Successfully Deleted' % taskToDelete.name)
        session.commit()
        return redirect(url_for('editCourseTasks', course_id=course_id))

@app.route('/courses/<int:course_id>/tasks/<int:task_id>/markComplete/', methods=['GET', 'POST'])
def markTaskComplete(course_id, task_id):
    '''
        Mark a task as complete
    '''
    task = session.query(Task).filter_by(task_id=task_id).one()
    if loggedin():
        user_id = getUserID(login_session["email"])
        try:
            completion = session.query(UserTask).filter_by(user_id=user_id, course_id=course_id, task_id=task_id).one()
        except:
            completion = UserTask(user_id=user_id, course_id=course_id, task_id=task_id)
        completion.completed = True
        session.add(completion)
        flash('%s Successfully Completed' % task.name)
        session.commit()

    return redirect(redirect_url())

@app.route('/courses/<int:course_id>/tasks/<int:task_id>/markIncomplete/', methods=['GET', 'POST'])
def markTaskIncomplete(course_id, task_id):
    '''
        Mark a task as complete
    '''
    if course_id is None or task_id is None:
        flash('Failed to mark task %s as incomplete' % task.name)
        return redirect(redirect_url())

    task = session.query(Task).filter_by(task_id=task_id).one()
    if loggedin():
        user_id = getUserID(login_session["email"])
        try:
            completion = session.query(UserTask).filter_by(user_id=user_id, course_id=course_id, task_id=task_id).one()
        except:
            completion = UserTask(user_id=user_id, course_id=course_id, task_id=task_id)
        completion.completed = False
        session.add(completion)
        flash('%s marked as incomplete' % task.name)
        session.commit()

    return redirect(redirect_url())

@app.route('/courses/<int:course_id>/editTasks')
def editCourseTasks(course_id):
    '''
        Edit a course's tasks
    '''
    if not isAdmin():
        return
    course = session.query(Course).filter_by(course_id=course_id).one()
    tasks = getTasksByCourse(course_id)
    return render_template('courseTasks.html',
        tasks=tasks,
        course=course,
        login_session=login_session)

@app.route('/courses/new/', methods=['POST'])
def newCourse():
    '''
        Create a new course
    '''
    if not isAdmin():
        return
    if request.method == 'POST':
        newCourse = Course(name=request.form['name'], description=request.form['description'])
        session.add(newCourse)
        flash('New Course %s Successfully Created' % newCourse.name)
        session.commit()
        return redirect(url_for('showCourses'))

@app.route('/courses.html')
def showCourses():
    '''
        Read courses
    '''
    courses = session.query(Course).order_by(asc(Course.name))
    return render_template('courses.html', courses=courses, login_session=login_session)

@app.route('/courses/<int:course_id>')
def viewCourse(course_id):
    '''
        View a specific course
    '''
    course = session.query(Course).filter_by(course_id=course_id).one()
    course.enrolled = loggedin() and userEnrolled(course_id, getUserID(login_session["email"]))
    tasks = getUserTasksByCourse(course_id, course.enrolled)
    return render_template('coursePage.html',
        tasks=tasks,
        course=course,
        login_session=login_session)

@app.route('/courses/<int:course_id>/edit/', methods=['POST'])
def editCourse(course_id):
    '''
        Update a course
    '''
    if not isAdmin():
        return
    editedCourse = session.query(Course).filter_by(course_id=course_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCourse.name = request.form['name']
        if request.form['description']:
            editedCourse.description = request.form['description']
        if request.form['url']:
            editedCourse.url = request.form['url']
        flash('Course Successfully Edited %s' % editedCourse.name)
        session.add(editedCourse)
        session.commit()
        return redirect(url_for('showCourses'))

@app.route('/courses/<int:course_id>/enroll/', methods=['POST'])
def enrollInCourse(course_id):
    '''
        Enroll in a course
    '''
    if request.method == 'POST':
        courseTasks = session.query(Task).filter_by(course_id=course_id).all()
        user_id = getUserID(login_session["email"])
        # Add uncompleted tasks for this course and user
        for task in courseTasks:
            userTask = UserTask(user_id=user_id, course_id=course_id, task_id=task.task_id)
            session.add(userTask)
        selectedCourse = session.query(Course).filter_by(course_id=course_id).one()
        newEnrollment = UserCourse(user_id=user_id, course_id=course_id)
        session.add(newEnrollment)
        session.commit()
        flash('Successfully enrolled in %s' % selectedCourse.name)
        return redirect(url_for('showCoursesPublic'))

@app.route('/courses/<int:course_id>/unenroll/', methods=['POST'])
def unenrollInCourse(course_id):
    '''
        Unenroll from a course
    '''
    if request.method == 'POST':
        # Delete enrolled tasks
        user_id = getUserID(login_session["email"])
        userTasks = session.query(UserTask).filter_by(user_id=user_id, course_id=course_id).all()
        for task in userTasks:
            session.delete(task)
        # Delte enrollment
        selectedCourse = session.query(Course).filter_by(course_id=course_id).one()
        user_id = getUserID(login_session["email"])
        enrollment = session.query(UserCourse).filter_by(course_id=course_id, user_id=user_id).all()[0]
        session.delete(enrollment)
        session.commit()
        flash('Successfully unenrolled from %s' % selectedCourse.name)
        return redirect(url_for('showCoursesPublic'))

@app.route('/courses/<int:course_id>/delete/', methods=['POST'])
def deleteCourse(course_id):
    '''
        Delete a course
    '''
    if not isAdmin():
        return
    courseToDelete = session.query(Course).filter_by(course_id=course_id).one()
    if request.method == 'POST':
        session.delete(courseToDelete)
        flash('%s Successfully Deleted' % courseToDelete.name)
        session.commit()
        return redirect(url_for('showCourses'))

@app.route('/majors/new/', methods=['POST'])
def newMajor():
    '''
        Create a new major
    '''
    if not isAdmin():
        return
    if request.method == 'POST':
        newMajor = Major(name=request.form['name'], description=request.form['description'])
        session.add(newMajor)
        flash('New Major %s Successfully Created' % newMajor.name)
        session.commit()
        return redirect(url_for('showMajors'))

@app.route('/majors.html')
def showMajors():
    '''
        Read majors
    '''
    majors = session.query(Major).order_by(asc(Major.name))
    return render_template('majors.html',
        majors=majors,
        login_session=login_session
    )

@app.route('/majors/<int:major_id>/edit/', methods=['POST'])
def editMajor(major_id):
    '''
        Update a major
    '''
    if not isAdmin():
        return
    if request.method == 'POST':
        editedMajor = session.query(Major).filter_by(major_id=major_id).one()
        if request.form['name']:
            editedMajor.name = request.form['name']
            flash('Major Successfully Edited %s' % editedMajor.name)
        if request.form['description']:
            editedMajor.description = request.form['description']
            flash('Major Successfully Edited %s' % editedMajor.name)
        session.add(editedMajor)
        session.commit()
        return redirect(url_for('showMajors'))

@app.route('/majors/<int:major_id>/delete/', methods=['POST'])
def deleteMajor(major_id):
    '''
    Delete a major
    '''
    if not isAdmin():
        return
    if request.method == 'POST':
        majorToDelete = session.query(Major).filter_by(major_id=major_id).one()
        session.delete(majorToDelete)
        flash('%s Successfully Deleted' % majorToDelete.name)
        session.commit()
        return redirect(url_for('showMajors', major_id=major_id))

@app.route('/majors/<int:major_id>/enroll/', methods=['POST'])
def enrollInMajor(major_id):
    '''
        Enroll in a major
    '''
    if request.method == 'POST':
        selectedMajor = session.query(Major).filter_by(major_id=major_id).one()
        user_id = getUserID(login_session["email"])
        newEnrollment = UserMajor(user_id=user_id, major_id=major_id)
        session.add(newEnrollment)
        session.commit()

        # Enroll in courses
        courses = getCoursesByMajor(major_id)
        for course in courses:
            enrollInCourse(course.course_id)

        flash('You have enrolled in %s' % selectedMajor.name)
        return redirect(url_for('showMajorsPublic'))

@app.route('/majors/<int:major_id>/unenroll/', methods=['POST'])
def unenrollFromMajor(major_id):
    '''
        Unenroll from a major
    '''
    if request.method == 'POST':
        selectedMajor = session.query(Major).filter_by(major_id=major_id).one()
        user_id = getUserID(login_session["email"])
        enrollment = session.query(UserMajor).filter_by(major_id=major_id, user_id=user_id).all()[0]
        session.delete(enrollment)
        session.commit()

        # Uenroll from courses
        courses = getCoursesByMajor(major_id)
        for course in courses:
            unenrollInCourse(course.course_id)

        flash('You have unenrolled from %s' % selectedMajor.name)
        return redirect(url_for('showMajorsPublic'))

@app.route('/majors/<int:major_id>/courses/')
def editMajorCourses(major_id):
    '''
        Edit courses for a major
    '''
    if not isAdmin():
        return
    courses = getCoursesByMajor(major_id)
    allCourses = session.query(Course).all()
    major = session.query(Major).filter_by(major_id=major_id).one()
    return render_template("majorCourses.html", 
        allCourses=allCourses,
        login_session=login_session,
        courses=courses,
        major=major)

@app.route('/majors/<int:major_id>/courses/add/', methods=['POST'])
def addCourseToMajor(major_id):
    '''
        Add a course to a major
    '''
    if not isAdmin():
        return
    course_id = request.form.get("courseId")
    course = session.query(Course).filter_by(course_id=course_id).one()
    addition = MajorCourse(major_id=major_id, course_id=course_id)
    session.add(addition)
    session.commit()

    flash('Successfully added course %s to major' % course.name)
    return redirect(url_for("editMajorCourses", major_id=major_id))

@app.route('/majors/<int:major_id>/courses/<int:course_id>/delete/', methods=["POST"])
def removeCourseFromMajor(major_id, course_id):
    '''
        Remove a course from a major
    '''
    if not isAdmin():
        return
    course = session.query(Course).filter_by(course_id=course_id).one()
    removal = session.query(MajorCourse).filter_by(major_id=major_id, course_id=course_id).one()
    session.delete(removal)
    session.commit()

    flash('Successfully removed course %s from major' % course.name)
    return redirect(url_for("editMajorCourses", major_id=major_id))

@app.route('/majors/<int:major_id>')
def viewMajor(major_id):
    '''
        View a specific major
    '''
    major = session.query(Major).filter_by(major_id=major_id).one()
    courses = getCoursesByMajor(major_id)
    return render_template('majorPage.html',
        courses=courses,
        major=major,
        login_session=login_session)

# Create anti-forgery state token
@app.route('/login.html')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', login_session=login_session, STATE=state, CLIENT_ID=CLIENT_ID)

def createUser(login_session):
    '''
        Create a user
    '''
    newUser = User(name=login_session["username"],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    try:
        # What happens if a user changes their email?
        # Can we get a different unique identifier?
        user = session.query(User).filter_by(email=login_session['email']).one()
        return user.user_id
    except:
        print "Error: Multiple users with same email"
        return None

@app.route('/users.html')
def showUsers():
    '''
        Read users
    '''
    users = session.query(User).order_by(asc(User.user_id))
    return render_template('users.html', users=users, login_session=login_session)

@app.route('/users/<int:user_id>/update/', methods=['POST'])
def editUser(user_id):
    '''
        Update a user
    '''
    if request.method == 'POST':
        if not isAdmin():
            return
        editedUser = session.query(User).filter_by(user_id=user_id).one()
        checklist = request.form.getlist("isAdmin")
        if len(checklist) > 0:
            editedUser.isAdmin = True
        else:
            editedUser.isAdmin = False
        flash('User %s Successfully Edited' % editedUser.name)
        session.add(editedUser)
        session.commit()
        return redirect(url_for('showUsers'))

@app.route('/users/<int:user_id>/delete/', methods=['POST'])
def deleteUser(user_id):
    '''
        Delete a user
    '''
    if request.method == 'POST':
        if not isAdmin():
            return
        userToDelete = session.query(User).filter_by(user_id=user_id).one()
        session.delete(userToDelete)
        flash('%s Successfully Deleted' % userToDelete.name)
        session.commit()
        return redirect(url_for('showUsers', user_id=user_id))



@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        print result.get('error')
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    #login_session['credentials'] = credentials
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    #userinfo_url = "https://www.googleapis.com/plus/v1/people/me"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params, verify=False) # NEEDS TO BE TRUE IN PRODUCTION, ADD SSL SUPPORT FIRST
    #https://urllib3.readthedocs.org/en/latest/security.html

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session["access_token"] = credentials.access_token

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    user = session.query(User).filter_by(user_id=user_id).one()
    login_session["isAdmin"] = user.isAdmin

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    #print 'In gdisconnect access token is %s', access_token
    #print 'User name is: ' 
    #print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    #print 'result is '
    #print result
    if result['status'] == '200':
        del login_session['access_token'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['isAdmin']
        #response = make_response(json.dumps('Successfully disconnected.'), 200)
        #response.headers['Content-Type'] = 'application/json'
        response = "<p>Disconnected successfully. Redirecting...</p>"
        response = response + "<script>setTimeout(function() {window.location.href = 'index.html';}, 4000);</script>"
        return response
    else:
        del login_session['access_token'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['isAdmin']
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

'''
# JSON API examples
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])
'''

def isComplete(task_id, course_id):
    '''
        Returns true if a user has completed a given task in a given course
    '''
    user_id = getUserID(login_session["email"])
    try:
        userTask = session.query(UserTask).filter_by(user_id=user_id, task_id=task_id, course_id=course_id).one()
        return userTask.completed
    except:
        return False

def isAdmin():
    '''
        Returns true if the current user is logged in as an admin
    '''
    return loggedin() and login_session["isAdmin"]

def loggedin():
    '''
        Returns true if the user is currently logged in
    '''
    return "email" in login_session

def getTask(task_id):
    task = session.query(Task).filter_by(task_id=task_id).one()
    return task

def getCoursesByMajor(major_id):
    ids = session.query(MajorCourse).filter_by(major_id=major_id).all()
    courses = []
    for assoc in ids:
        course = session.query(Course).filter_by(course_id=assoc.course_id).one()
        courses.append(course)
    return courses

def userEnrolled(course_id, user_id):
    if user_id is None:
        return False
    results = session.query(UserCourse).filter_by(course_id=course_id, user_id=user_id).all()
    return len(results) > 0

def getUserTasksByCourse(course_id, enrolled=True):
    if not loggedin() or not enrolled:
        return session.query(Task).filter_by(course_id=course_id).all()
    user_id = getUserID(login_session["email"])
    tasks = session.query(UserTask).filter_by(user_id=user_id, course_id=course_id).all()
    for userTask in tasks:
        task = session.query(Task).filter_by(task_id=userTask.task_id).one()
        userTask.name = task.name
        userTask.url = task.url

    return tasks

def courseProgress(course_id):
    tasks = getUserTasksByCourse(course_id)
    if len(tasks) == 0:
        return 0
    total = 0.0;
    for task in tasks:
        if task.completed:
            total += 1.0
    return floor(total / len(tasks) * 100)

def getTasksByCourse(course_id):
    '''
        Returns a list of tasks for a given course id
    '''
    tasks = session.query(Task).filter_by(course_id=course_id).all()
    return tasks

def getTopUnfinishedTasks():
    '''
        Returns a list of the next unfininished tasks for each enrolled course
    '''
    if not loggedin():
        return []
    tasks = []
    user_id = getUserID(login_session["email"])
    courses = session.query(UserCourse).filter_by(user_id=user_id).all()
    for course in courses:
        courseTasks = getUserTasksByCourse(course.course_id)
        for i in range(len(courseTasks)):
            task = courseTasks[i]
            if not task.completed:
                tasks.append(task)
                break
    return tasks

def getEnrolledCourses():
    '''
        Returns a list of the courses enrolled in by the current user
    '''
    if not loggedin():
        return []
    user_id = getUserID(login_session["email"])
    associations = session.query(UserCourse).filter_by(user_id=user_id).all()
    enrolled_courses = []
    for association in associations:
        course_id = association.course_id
        course = session.query(Course).filter_by(course_id=course_id).one()
        enrolled_courses.append(course)
    return enrolled_courses

def majorProgress(major_id):
    '''
        Returns the user's progress in a given major as a number between 0 and 1
    '''
    courses = session.query(MajorCourse).filter_by(major_id=major_id).all()
    progress = 0.0
    if len(courses) > 0:
        for course in courses:
            progress += courseProgress(course.course_id) / 100.0
        progress /= len(courses)
    return progress

def getEnrolledMajors():
    '''
        Returns a list of the majors that the current user is enrolled in
    '''
    if not loggedin():
        return []
    user_id = getUserID(login_session["email"])
    associations = session.query(UserMajor).filter_by(user_id=user_id).all()
    enrolled_majors = []
    for association in associations:
        major_id = association.major_id
        # Compute major progress
        progress = majorProgress(major_id)
        major = session.query(Major).filter_by(major_id=major_id).one()
        major.progress = progress * 100.0
        enrolled_majors.append(major)
    return enrolled_majors

def getUserInfo(user_id):
    user=session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    '''
        Returns the user ID associated with an email
    '''
    try:
        user=session.query(User).filter_by(email=email).one()
        return user.user_id
    except:
        return None

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

if __name__ == '__main__':
    app.secret_key = 'P0HROJGcAoglvmXBtwjLC69v'
    app.debug = False
    #context = SSL.Context(SSL.SSLv23_METHOD)
    #context.use_privatekey_file('/home/john/Desktop/onlineU/server.key')
    #context.use_certificate_file('/home/john/Desktop/onlineU/server.crt')
    app.run(
        host=HOST,
        port=PORT)
