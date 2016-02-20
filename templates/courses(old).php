<h2>Top Educational Sites</h2>
        <p>Sites sorted by rating</p>
        <p>Allow users to rate sites</p>
        <?php
            if (!$link = mysql_connect('127.0.0.1', 'root', 'snes1994')) {
                echo 'Could not connect to mysql';
                exit;
            }

            if (!mysql_select_db('main_database', $link)) {
                echo 'Could not select database';
                exit;
            }

            $sql    = 'SELECT * FROM sites LIMIT 20';
            $result = mysql_query($sql, $link);

            if (!$result) {
                echo "DB Error, could not query the database\n";
                echo 'MySQL Error: ' . mysql_error();
                exit;
            }

            echo "<ol>";
            while ($row = mysql_fetch_assoc($result)) {
                echo "<li><a href='";
                echo $row["site"];
                echo "'>";
                echo $row["name"];
                echo "</a></li>";
            }
            echo "</ol>";

            mysql_free_result($result);
        ?>
        <h2>Courses</h2>
        <p>Search course database by various features and tags</p>
        <form>
            <label><input type="checkbox">Self-paced</label>
            <label><input type="checkbox">Graded exams</label>
            <label><input type="checkbox">Certificate of completion</label>
            <br>
            Tags: <input type="text">
            <br>
            <button type="button">Search</button>
        </form>
        <p>Results go here</p>