# Online U

[![Join the chat at https://gitter.im/jdsutton/OnlineU](https://badges.gitter.im/jdsutton/OnlineU.svg)](https://gitter.im/jdsutton/OnlineU?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This is a website for free, curated online courses.

How it's unique:
* It is 100% free. There will be no charge to earn certificates.
* It's long-term goal is to offer comprehensive college-level curriculum for a wide variety of topics.
* Courses will be graded and allow students to go back and improve their grades.
* Courses are grouped by major and ordered coherently, instead of a grab-bag.
* It tracks student progress and will offer automatically graded exams, adding a layer of usefulness to sites like [MIT OCW](http://ocw.mit.edu/index.htm) which have good content but lack these features.

![site image](http://i.imgur.com/VFW8CRS.png)

## Dependencies
* Python 2.x
* [Flask](http://flask.pocoo.org/)
* [SQLAlchemy](http://www.sqlalchemy.org/)
* [oauth2client](https://github.com/google/oauth2client)

All dependencies (besides Python) can be installed by running pip install -r requirements.txt

## Initializing the database
`$ python database_setup.py`

## Creating credentials
1. Go to https://console.developers.google.com
2. Create a new project
3. Click "enable and manage APIs"
4. Click "credentials"
5. Create credentials --> OAuth client ID --> Web applications
6. Add your access point to the authorized javascript origins (your public IP, 127.0.0.1, localhost, etc)
7. Add a placeholder site under "Authorized redirect URIs", eg: http://www.example.com
8. Save the credentials file as `client_secrets.json` in the main directory.

## Adding more courses (optional)
`$ sudo python`
```
>>>from database_setup import addCourses
>>># page = one of the links from http://ocw.mit.edu/courses/find-by-department/
>>>addCourses(page)
>>>exit()
```

## Starting the server
`$ sudo python project.py`

## Contributing

Contributions from anyone are welcomed and very appreciated! This is a very big project and it's going to take a lot of people to make it work. Take a look at TODO.md and the issues page for ideas on how to help.
