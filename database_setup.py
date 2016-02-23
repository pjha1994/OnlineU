from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

DATABASE_NAME = "main_database.db"

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
    user_id = Column(Integer, nullable=False)
    course_id = Column(Integer, nullable=False)
    task_id = Column(Integer, nullable=False)
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

    courses = ["Computer Programming"]

    # Add majors
    for major in majors:
        newMajor = Major(
            name=major,
            description=""
        )
        session.add(newMajor)

    for course in courses:
        newCourse = Course(
            name=course,
            description=""
        )
        session.add(newCourse)


    admin = User(name="John Sutton", email="jdsutton@calpoly.edu", picture="https://lh4.googleusercontent.com/-C6cSzCA5-Bw/AAAAAAAAAAI/AAAAAAAACVo/OrC0MgMptnI/photo.jpg", isAdmin=True)
    session.add(admin)

    session.commit()

