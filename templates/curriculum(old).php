<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <h2>Curriculum</h2>
        <p>Use the interface below to enroll in a degree program.</p>
        <?php
            if (!$link = mysql_connect('127.0.0.1', 'root', 'snes1994')) {
                echo 'Could not connect to mysql';
                exit;
            }

            if (!mysql_select_db('main_database', $link)) {
                echo 'Could not select database';
                exit;
            }

            $sql    = 'SELECT * FROM curriculum ORDER BY name LIMIT 20';
            $result = mysql_query($sql, $link);

            if (!$result) {
                echo "DB Error, could not query the database\n";
                echo 'MySQL Error: ' . mysql_error();
                exit;
            }

            echo "<ol>";
            while ($row = mysql_fetch_assoc($result)) {
                $curriculum_name = $row["name"];
                echo "<li>";
                echo "<button type='button' onclick='unhide(\"" . $curriculum_name . "\")' class='expandButton'>" . $curriculum_name . "</button>";
                echo "<button type='button' class='enrollButton'>Enroll</button>";

                $module_name   = $row["module_name"];
                $sql = "SELECT * FROM " . $module_name . ";";

                $modules = mysql_query($sql);
                if (!$modules) {
                    echo "DB Error, could not query the database\n";
                    echo 'MySQL Error: ' . mysql_error();
                    exit;
                }

                echo "<br><ol id='" . $curriculum_name . "' class='hiddenList'>";
                while ($module = mysql_fetch_assoc($modules)) {
                    $module_name = $module["module_name"];
                    echo "<li style='display:none'>";
                    echo $module_name;
                    echo "</li>";
                }
                echo "</ol>";
                echo "</li>";
            }
            echo "</ol>";

            mysql_free_result($result);
        ?>

        <script>
            function unhide(id) {
                element = document.getElementById(id);
                children = element.getElementsByTagName("li")
;
                for (var i in children) {
                    if (children[i].style) {
                        if (children[i].style.display=="none") {
                            children[i].style.display="block";
                        }
                        else {
                            children[i].style.display="none";
                        }
                    }
                }
            }
        </script>
    </body>
</html>