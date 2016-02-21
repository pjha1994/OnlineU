# Online U

This is a website for free, curated online courses. 

## Starting the server
* If you want the G+ login to work, you will need to create a client_secrets.json file using https://console.developers.google.com

sudo python project.py

## Todo:
* Courses
  * Create a course template page
  * Show course link and exams for course on course page
  * Show completed courses on user profile
  * Add support for integrating our own course material
* Majors
  * Add support for optional and required minors
  * Create major template page
  * Allow courses to be added to the major via admin page
  * Automatically enroll user in all courses for a major when the user enrolls in that major
  * Track user progress through majors
* Exams
  * Allow admins to edit exams online
  * Add suport for math expressions
  * Add support for multiple choice questions
  * Create server-side grading script
  * Figure out ways to prevent cheating
  * Add support for randomized questions and random question selection
* Misc
  * Make the site look nicer
  * Issue verified certificates upon degree completion.
  * SSL/HTTPS
