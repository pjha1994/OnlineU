import sys
import urllib2
from lxml import html, etree
import re

MAIN_PAGE = "http://ocw.mit.edu"
URL = "http://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-042j-mathematics-for-computer-science-fall-2010/index.htm"
COURSES_PAGE = "http://ocw.mit.edu/courses/"

class Course():
    def __init__(self, title, description, url, instructors, cal, assignments, lec):
        self.title = title
        self.description = description
        self.url = url
        self.instructors = instructors
        self.calendar = cal
        self.assignments = assignments
        self.lectures = lec

    def __repr__(self):
        # Title
        s = "Title: " + self.title + "\n"
        # Course URL
        s = s + "URL: " + self.url + "\n"
        # Instructors
        s = s + "Instructor(s):\n"
        for instructor in self.instructors:
            s = s + instructor + "\n"
        # Calendar
        s = s + "Calendar:\n"
        for entry in self.calendar:
            for part in entry:
                try:
                    s = s + str(part) + "   "
                except UnicodeEncodeError:
                    continue
            s = s + "\n"
        # Lectures
        s = s + "Lectures:\n"
        for lecture in self.lectures:
            s = s + lecture[0] + "\n"
        # Assignments
        s = s + "Assignments:\n"
        for a in self.assignments:
            s = s + str(a[2]) + "\n"
        return s

    def getSchedule():
        pass

def cleanURL(url):
    url = re.sub("index.*", "", url)
    if not url.endswith("/"):
        url = url + "/"

    return url

def calendar(url):
    return cleanURL(url) + "calendar"

def assignments(url):
    return cleanURL(url) + "assignments"

def lectures2(url):
    return cleanURL(url) + "video-lectures"

def lectures(url):
    return cleanURL(url) + "lecture-videos"

def loadPage(url):
    #print "Loading " + url
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response.read()

def getAllCoursePages():
    page = loadPage(COURSES_PAGE)
    tree = html.fromstring(page)
    links = tree.xpath('//a[@class="preview"]')
    pages = []
    for link in links:
        href = link.attrib["href"]
        if href.startswith("/courses"):
            pages.append(MAIN_PAGE + href)
    return pages


def main(args):
    if len(args) > 0:
        URL = args[0]

    # Load the main coursepage
    page = loadPage(URL)

    # Parse the webpage
    #print "Scraping page"
    tree = html.fromstring(page)
    title = tree.xpath('//h1/text()')[0]
    print "  " + title

    instructors = tree.xpath('//p[@class="ins"]/text()')
    description = tree.xpath('//div[@id="description"]/div/p/text()')[0]

    cal = []
    try:
        # Load calendar
        page = loadPage(calendar(URL))
        tree = html.fromstring(page)
        rows = tree.xpath('//tr')

        # Parse calendar
        for row in rows:
            crow = []
            for element in row:
                crow.append(element.text)
            try:
                crow[0] = int(crow[0])
            except TypeError:
                continue
            except ValueError:
                continue
            cal.append(crow)
    except urllib2.HTTPError:
        pass

    c = []
    try:
        # Load assignments
        page = loadPage(assignments(URL))
        tree = html.fromstring(page)
        rows = tree.xpath('//tr')

        # Parse assignments
        for row in rows:
            crow = []
            for element in row:
                crow.append(element.text)
                for sub in element:
                    if sub.tag == "a":
                        crow.append(sub.attrib['href'])
            try:
                crow[0] = int(crow[0])
            except TypeError:
                continue
            except ValueError:
                continue
            c.append(crow)
    except urllib2.HTTPError:
        pass

    # Load lectures
    try:
        page = loadPage(lectures(URL))
        tree = html.fromstring(page)
        ls = tree.xpath('//div[@class="medialisting"]')
    except:
        print "  Could not load: " + lectures(URL)
        try:
            page = loadPage(lectures2(URL))
            print "  Loaded alternative page"
            tree = html.fromstring(page)
            ls = tree.xpath('//div[@class="medialisting"]')
        except:
            print "  Could not load: " + lectures2(URL)
            print "  Failed to load lectures page"
            ls = []
    print "  Lectures found: " + str(len(ls))

    # Parse lectures
    result = []
    for lecture in ls:
        link = lecture[0].attrib['href']
        t = lecture[0].attrib['title']
        if link.startswith("/"):
            result.append([t, "http://ocw.mit.edu" + link])
        else:
            result.append([t, link])

    # Compile everything together
    course = Course(title, description, URL, instructors, cal, c, result)
    return course


if __name__ == "__main__":
    main(sys.argv[1:])