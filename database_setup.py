from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

DATABASE_NAME = "main_database.db"

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
    One component of a course
    Eg: a video, an assignment, a reading, etc.
'''
class Task(Base):
    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True)
    name = Column(String(250))
    url = Column(String(250), nullable=False)

'''
    Table of online courses
'''
class Course(Base):
    __tablename__ = 'courses'

    course_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    url = Column(String(250))
    description = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.course_id,
            'url': self.url
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