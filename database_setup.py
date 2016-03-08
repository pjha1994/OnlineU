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
    algorithms = Course(name="Introduction to Algorithms",
        description="Learn about algorithms: the tools used by computer scientists to solve problems.")
    session.add(algorithms)
    csmath = Course(name="Mathematics for Computer Science",
        description="Learn the mathematical foundation for computer science.")
    session.add(csmath)

    # Add tasks
    task = Task(course_id=1,
        name="Lecture 1: Algorithmic Thinking, Peak Finding",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-1-algorithmic-thinking-peak-finding")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 2: Models of Computation, Document Distance",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-2-models-of-computation-document-distance")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 3: Insertion Sort, Merge Sort",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-3-insertion-sort-merge-sort")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 4: Heaps and Heap Sort",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-4-heaps-and-heap-sort")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 5: Binary Search Trees, BST Sort",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-5-binary-search-trees-bst-sort")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 6: AVL Trees, AVL Sort",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-6-avl-trees-avl-sort")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 7: Counting Sort, Radix Sort, Lower Bounds for Sorting",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-7-counting-sort-radix-sort-lower-bounds-for-sorting")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 8: Hashing with Chaining",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-8-hashing-with-chaining")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 9: Table Doubling, Karp-Rabin",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-9-table-doubling-karp-rabin")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 10: Open Addressing, Cryptographic Hashing",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-10-open-addressing-cryptographic-hashing")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 11: Integer Arithmetic, Karatsuba Multiplication",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-11-integer-arithmetic-karatsuba-multiplication")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 12: Square Roots, Newton's Method",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-12-square-roots-newtons-method")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 13: Breadth-First Search (BFS)",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-13-breadth-first-search-bfs")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 14: Depth-First Search (DFS), Topological Sort",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-14-depth-first-search-dfs-topological-sort")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 15: Single-Source Shortest Paths Problem",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-15-single-source-shortest-paths-problem")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 16: Dijkstra",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-16-dijkstra")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 17: Bellman-Ford",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-17-bellman-ford")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 18: Speeding up Dijkstra",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-18-speeding-up-dijkstra")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 19: Dynamic Programming I: Fibonacci, Shortest Paths",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-19-dynamic-programming-i-fibonacci-shortest-paths")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 20: Dynamic Programming II: Text Justification, Blackjack",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-20-dynamic-programming-ii-text-justification-blackjack")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 21: Dynamic Programming III: Parenthesization, Edit Distance, Knapsack",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-21-dp-iii-parenthesization-edit-distance-knapsack")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 22: Dynamic Programming IV: Guitar Fingering, Tetris, Super Mario Bros.",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-22-dp-iv-guitar-fingering-tetris-super-mario-bros")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 23: Computational Complexity",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-23-computational-complexity")
    session.add(task)
    task = Task(course_id=1,
        name="Lecture 24: Topics in Algorithms Research",
        url="http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms-fall-2011/lecture-videos/lecture-24-topics-in-algorithms-research")
    session.add(task)


    session.commit()

