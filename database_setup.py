from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, "./MITscraper")
import scraper

Base = declarative_base()

DATABASE_NAME = "main_database.db"

class Exam(Base):
    __tablename__ = "exams"
    exam_id = Column(Integer, primary_key=True)
    exam_title = Column(String(250))

class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    question_id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.exam_id'), nullable=False)
    answer = Column(String(250))

'''
    Association table for courses in majors
'''
class MajorCourse(Base):
    __tablename__ = "major_courses"

    id = Column(Integer, primary_key=True)
    major_id = Column(Integer, ForeignKey('majors.major_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)

'''
    Association table for user course enrollments
'''
class UserCourse(Base):
    __tablename__ = "user_courses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    user_progress = Column(Integer, default=0)

'''
    Association table for user major enrollments
'''
class UserMajor(Base):
    __tablename__ = "user_majors"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    major_id = Column(Integer, ForeignKey('majors.major_id'), nullable=False)
    user_progress = Column(Integer, default=0)

'''
    Table of site users
'''
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(250))
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    isAdmin = Column(Boolean, default=False)

'''
    Association table for individual tasks
'''
class UserTask(Base):
    __tablename__ = 'user_tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    course_id = Column(Integer,ForeignKey('courses.course_id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.task_id'), nullable=False)
    grade = Column(Float)
    completed = Column(Boolean, default=False)

'''
    One component of a course
    Eg: a video, an assignment, a reading, etc.
'''
class Task(Base):
    __tablename__ = "tasks"
    
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    task_id = Column(Integer, primary_key=True)
    isGraded = Column(Boolean, default=False)
    name = Column(String(250))
    url = Column(String(250), nullable=False)

'''
    Table of online courses
'''
class Course(Base):
    __tablename__ = 'courses'

    course_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.course_id
        }

'''
    Table of curriculumn programs
'''
class Major(Base):
    __tablename__ = 'majors'

    major_id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'major_id': self.major_id
        }

engine = create_engine('sqlite:///' + DATABASE_NAME)
Base.metadata.create_all(engine)

if __name__ == "__main__":

    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    majors = ["Biology", "Computer Science", "Paleontology", "Philosophy", "Sociology", "Accounting", 
    "Archaeology", "Geology", "Computer Engineeering",
    "History", "Oceanography", "Environmental Science", "Political Science", "Chemistry",
    "Physics", "Mathematics", "Mechanical Engineering"]

    # Add majors
    for major in majors:
        newMajor = Major(
            name=major,
            description=""
        )
        session.add(newMajor)

    # Add users
    admin = User(name="John Sutton", email="jdsutton@calpoly.edu", picture="https://lh4.googleusercontent.com/-C6cSzCA5-Bw/AAAAAAAAAAI/AAAAAAAACVo/OrC0MgMptnI/photo.jpg", isAdmin=True)
    session.add(admin)

    # Add courses
    print "Locating course pages"
    page = "http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/"
    coursesToAdd = scraper.getAllCoursePages(page)

    print "Locating course lecture videos"
    major_id = majors.index("Computer Science") + 1
    course_id = 1
    for url in coursesToAdd:
        course = scraper.main([url])
        if len(course.lectures) == 0:
            continue
        print "Creating course: " + course.title
        c = Course(name=course.title, description=course.description)
        session.add(c)
        #rel = MajorCourse(major_id=2, course_id=course_id)
        #session.add(rel)
        for lecture in course.lectures:
            task = Task(course_id=course_id,
                name=lecture[0],
                url=lecture[1]
            )
            session.add(task)
        course_id += 1

        session.commit()
