from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, send_from_directory
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import *
from flask import session as login_session
import random
import string
import os
from OpenSSL import SSL

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
app._static_folder = "~/Desktop/onlineU/static"

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

@app.route("/css/<path:path>")
def sendStaticFile(path):
    return send_from_directory("static", path)

@app.route('/')
@app.route('/index.html')
def showHomepage():
    enrolled_majors = getEnrolledMajors()
    enrolled_courses = getEnrolledCourses()
    return render_template('index.html', login_session=login_session, enrolled_majors=enrolled_majors, enrolled_courses=enrolled_courses)

@app.route('/profile.html')
def showProfile():
    enrolled_majors = getEnrolledMajors()
    enrolled_courses = getEnrolledCourses()
    return render_template('profile.html', login_session=login_session, enrolled_majors=enrolled_majors, enrolled_courses=enrolled_courses)

@app.route('/volunteer.html')
def showVolunteerPage():
    # return "The current session state is %s" % login_session['state']
    return render_template("volunteer.html", login_session=login_session)

@app.route('/admin.html')
def showAdminPage():
    # return "The current session state is %s" % login_session['state']
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

'''
    Create a new course
'''
@app.route('/courses/new/', methods=['POST'])
def newCourse():
    if request.method == 'POST':
        newCourse = Course(name=request.form['name'], description=request.form['description'], url=request.form['url'])
        session.add(newCourse)
        flash('New Course %s Successfully Created' % newCourse.name)
        session.commit()
        return redirect(url_for('showCourses'))

'''
    Read courses
'''
@app.route('/courses.html')
def showCourses():
    courses = session.query(Course).order_by(asc(Course.name))
    return render_template('courses.html', courses=courses)

'''
    Update a course
'''
@app.route('/courses/<int:course_id>/edit/', methods=['POST'])
def editCourse(course_id):
    editedCourse = session.query(Course).filter_by(course_id=course_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCourse.name = request.form['name']
            flash('Course Successfully Edited %s' % editedCourse.name)
        if request.form['description']:
            editedCourse.description = request.form['description']
            flash('Course Successfully Edited %s' % editedCourse.name)
        if request.form['url']:
            editedCourse.url = request.form['url']
            flash('Course Successfully Edited %s' % editedCourse.name)
        session.add(editedCourse)
        session.commit()
        return redirect(url_for('showCourses'))

'''
    Enroll in a course
'''
@app.route('/courses/<int:course_id>/enroll/', methods=['POST'])
def enrollInCourse(course_id):
    if request.method == 'POST':
        selectedCourse = session.query(Course).filter_by(course_id=course_id).one()
        user_id = getUserID(login_session["email"])
        newEnrollment = UserCourse(user_id=user_id, course_id=course_id)
        session.add(newEnrollment)
        session.commit()
        return redirect(url_for('showCoursesPublic'))

'''
    Unenroll from a course
'''
@app.route('/courses/<int:course_id>/unenroll/', methods=['POST'])
def unenrollInCourse(course_id):
    if request.method == 'POST':
        selectedCourse = session.query(Course).filter_by(course_id=course_id).one()
        user_id = getUserID(login_session["email"])
        enrollment = session.query(UserCourse).filter_by(course_id=course_id, user_id=user_id).all()[0]
        session.delete(enrollment)
        session.commit()
        return redirect(url_for('showCoursesPublic'))

'''
    Create a new major
'''
@app.route('/majors/new/', methods=['POST'])
def newMajor():
    if request.method == 'POST':
        newMajor = Major(name=request.form['name'], description=request.form['description'])
        session.add(newMajor)
        flash('New Major %s Successfully Created' % newMajor.name)
        session.commit()
        return redirect(url_for('showMajors'))

'''
    Read majors
'''
@app.route('/majors.html')
def showMajors():
    majors = session.query(Major).order_by(asc(Major.name))
    return render_template('majors.html', majors=majors)

'''
    Update a major
'''
@app.route('/majors/<int:major_id>/edit/', methods=['POST'])
def editMajor(major_id):
    editedMajor = session.query(Major).filter_by(major_id=major_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedMajor.name = request.form['name']
            flash('Major Successfully Edited %s' % editedMajor.name)
        if request.form['description']:
            editedMajor.description = request.form['description']
            flash('Major Successfully Edited %s' % editedMajor.name)
        session.add(editedMajor)
        session.commit()
        return redirect(url_for('showMajors'))

'''
    Delete a major
'''
@app.route('/majors/<int:major_id>/delete/', methods=['POST'])
def deleteMajor(major_id):
    majorToDelete = session.query(Major).filter_by(major_id=major_id).one()
    if request.method == 'POST':
        session.delete(majorToDelete)
        flash('%s Successfully Deleted' % majorToDelete.name)
        session.commit()
        return redirect(url_for('showMajors', major_id=major_id))

'''
    Enroll in a major
'''
@app.route('/majors/<int:major_id>/enroll/', methods=['POST'])
def enrollInMajor(major_id):
    if request.method == 'POST':
        selectedMajor = session.query(Major).filter_by(major_id=major_id).one()
        user_id = getUserID(login_session["email"])
        newEnrollment = UserMajor(user_id=user_id, major_id=major_id)
        session.add(newEnrollment)
        session.commit()
        return redirect(url_for('showMajorsPublic'))

'''
    Unenroll from a major
'''
@app.route('/majors/<int:major_id>/unenroll/', methods=['POST'])
def unenrollFromMajor(major_id):
    if request.method == 'POST':
        selectedMajor = session.query(Major).filter_by(major_id=major_id).one()
        user_id = getUserID(login_session["email"])
        enrollment = session.query(UserMajor).filter_by(major_id=major_id, user_id=user_id).all()[0]
        session.delete(enrollment)
        session.commit()
        return redirect(url_for('showMajorsPublic'))

# Create anti-forgery state token
@app.route('/login.html')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

'''
    Create a user
'''
def createUser(login_session):
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

'''
    Read users
'''
@app.route('/users.html')
def showUsers():
    users = session.query(User).order_by(asc(User.user_id))
    return render_template('users.html', users=users)

'''
    Delete a user
'''
@app.route('/users/<int:user_id>/delete/', methods=['POST'])
def deleteUser(user_id):
    userToDelete = session.query(User).filter_by(user_id=user_id).one()
    if request.method == 'POST':
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

    # login_session["isAdmin"] = ...

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
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

'''
# JSON APIs to view Restaurant Information
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


# Show all restaurants
@app.route('/')
def showRestaurants():
    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
    return render_template('index.html', restaurants=restaurants)

# Create a new restaurant


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['name'])
        session.add(newRestaurant)
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

# Edit a restaurant


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=editedRestaurant)


# Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)

# Show a restaurant menu


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return render_template('menu.html', items=items, restaurant=restaurant)


# Create a new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], description=request.form[
                           'description'], price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Edit a menu item


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):

    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


# Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)
'''

def loggedin():
    return "email" in login_session

def getEnrolledCourses():
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

def getEnrolledMajors():
    if not loggedin():
        return []
    user_id = getUserID(login_session["email"])
    associations = session.query(UserMajor).filter_by(user_id=user_id).all()
    enrolled_majors = []
    for association in associations:
        major_id = association.major_id
        major = session.query(Major).filter_by(major_id=major_id).one()
        enrolled_majors.append(major)
    return enrolled_majors

def getUserInfo(user_id):
    user=session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user=session.query(User).filter_by(email=email).one()
        return user.user_id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'P0HROJGcAoglvmXBtwjLC69v'
    app.debug = True
    #context = SSL.Context(SSL.SSLv23_METHOD)
    #context.use_privatekey_file('/home/john/Desktop/onlineU/server.key')
    #context.use_certificate_file('/home/john/Desktop/onlineU/server.crt')
    app.run(host=HOST, port=PORT)