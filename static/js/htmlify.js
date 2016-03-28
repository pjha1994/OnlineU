/**
    This library contains functions for converting markdown to HTML
**/

function htmlify(source, target) {
    /**
        Get text from source
        Compile it to HTML
        Insert it into target
    **/

    target = target || source;

    var markdown = source.value;
    var html = "";
    var lines = markdown.split("\n");

    // Compile to html
    var line;
    var hCount;
    for (var i = 0; i < lines.length; i++) {
        line = lines[i];
        line = line.trim();

        // Check for headers
        hCount = 0;
        while (line[0] === "#") {
            hCount++;
            line = line.substr(1, line.length);
        }
        if (hCount > 0) {
            html = html + "<h" + hCount + ">";
            html = html + line;
            html = html + "</h" + hCount + ">";
            continue;
        }

        // Paragraph
        html = html + "<p>" + line + "</p>";

    }

    target.innerHTML = html;
};

function link(source, target) {
    /**
        Automatically compile from source to target when the user types
    **/
    source.onkeyup = function() {
        htmlify(source, target);
    };
};