function Question() {
    var description = "";
    var answer = "";
    var id = Question.id;
    Question.id++;

    // Grab typed in info
    this.update = function() {
        description = document.getElementById("description" + id).value;
        var publicDescription = document.getElementById("publicDescription" + id);
        publicDescription.innerHTML = description;
        answer = document.getElementById("answer" + id).value;
    };

    // Return a HTML string representing the question
    this.render = function() {
        console.log(description)
        var s = "";
        s = s + "<div class='examQuestion' id='" + id + "'>";
        s = s + "<h3>Question " + (id + 1) + ":</h3>";
        s = s + "<h4>Description:</h4>";
        s = s + "<textarea onkeyup='updateAll();' id='description" + id + "'></textarea>";
        s = s + "<h4>Answer:</h4>";
        s = s + "<input type='text' id='answer" + id + "'></input>"
        s = s + "</div>";
        return s;
    };

    this.renderPublic = function() {
        var s = "";
        s = s + "<div class='examQuestion' id='" + id + "'>";
        s = s + "<h3>Question " + (id + 1) + ":</h3>";
        s = s + "<h4>Description:</h4>";
        s = s + "<p id='publicDescription" + id + "'</p>";
        s = s + "<h4>Answer:</h4>";
        s = s + "<input type='text' id='publicAsnswer" + id + "'></input>"
        s = s + "</div>";
        return s;
    };
};
Question.id = 0;

function Exam() {
    var title = "New Exam";
    var questions = [];

    this.updateAll = function() {
        var titleEntry = document.getElementById("title");
        var titleLabel = document.getElementById("titlePublic");
        if (titleEntry) {
            title = titleEntry.value;
            titleLabel.innerHTML = title;
        }
        for (var i = 0; i < questions.length; i++) {
            questions[i].update();
        }
    };

    // Compile all questions to HTML and place them in the div
    this.render = function(divID) {
        divID = divID || "exam";
        var s = "";
        s = s + "<input class='titleInput' onkeyup='updateAll();' type='text' id='title' value='" + title + "'></input>"

        for (var i = 0; i < questions.length; i++) {
            s = s + questions[i].render();
        }

        var div = document.getElementById(divID);
        div.innerHTML = s;
    };

    this.renderPublic = function(divID) {
        divID = divID || "examPreview";

        var s = "";
        s = s + "<h2 id='titlePublic'>" + title + "</h2>"

        for (var i = 0; i < questions.length; i++) {
            s = s + questions[i].renderPublic();
        }

        var div = document.getElementById(divID);
        div.innerHTML = s;
    }

    // Create a new question
    this.addQuestion = function() {;
        questions.push(new Question());
        this.render();
        this.renderPublic();
    };

    // Remove the last question
    this.deleteQuestion = function() {;
        if (questions.length === 0) return;
        Question.id--;
        questions.pop(questions.length - 1);
        this.render();
        this.renderPublic();
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