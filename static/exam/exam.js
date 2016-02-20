function Question() {
    var description = "";
    var answer = null;
    var id = Question.id;
    Question.id++;

    // Return a HTML string representing the question
    this.render = function() {
        var s = "";
        s = s + "<div class='examQuestion' id='" + id + "'>";
        s = s + "<h3>Question " + (id + 1) + ":</h3>";
        s = s + "<h4>Description:</h4>";
        s = s + "<textarea id='description" + id + "'></textarea>";
        s = s + "<h4>Answer:</h4>";
        s = s + "<input type='text' id='answer" + id + "'></input>"
        s = s + "</div>";
        return s;
    };
};
Question.id = 0;

function Exam() {
    var title = "New Exam";
    var questions = [];

    // Compile all questions to HTML and place them in the div
    this.render = function(divID) {
        divID = divID || "exam";
        var s = "";
        s = s + "<h2>" + title + "</h2>"

        for (var i = 0; i < questions.length; i++) {
            s = s + questions[i].render();
        }

        var div = document.getElementById(divID);
        div.innerHTML = s;
    };

    // Create a new question
    this.addQuestion = function() {;
        questions.push(new Question());
        this.render();
    };

    // Save the exam to the server
    this.save = function() {

    }

    // Load the exam from the server
    this.load = function() {

    }

    // Submit answers to server for grading
    this.grade = function() {

    }
};