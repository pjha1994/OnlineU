# Online U

This is a website for free, curated online courses. 

## Initializing the database
python database_setup.py

## Starting the server
* If you want the G+ login to work, you will need to create a client_secrets.json file using https://console.developers.google.com

sudo python project.py

## Todo:
* Courses
  * Show course progress on course page, homepage, profile
  * Show next unfinished task for each course on the homepage
  * Show completed courses on user profile
* Majors
  * Allow courses to be added to the major via admin page
  * Automatically enroll user in all courses for a major when the user enrolls in that major
  * Add support for optional and required minors
* Exams
  * Allow admins to edit exams online
  * Add suport for math expressions
  * Add support for multiple choice questions
  * Create server-side grading script
  * Figure out ways to prevent cheating
  * Add support for randomized questions and random question selection
* Misc
  * Add a donation page
  * Add application form for volunteer content curators
  * Add bug reporting
  * Issue verified certificates upon degree completion.
  * SSL/HTTPS
