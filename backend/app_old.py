HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthHack</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            max-width: 80%;
            width: 80%;
            position: relative;
        }
        .fixed-top-form {
            position: sticky;
            top: 0;
            background: white;
            padding-bottom: 10px;
            z-index: 1000;
            border-bottom: 2px solid #ddd;
        }
        .scrollable-list {
            max-height: 500px;
            overflow-y: auto;
            margin-top: 15px;
            padding-right: 5px;
            display: flex;
            flex-direction: column-reverse;
        }
    </style>
</head>
<body>
    <div class="container text-center">
        <div class="fixed-top-form">
            <h2 class="mb-4">Flask Input Form</h2>
            <form method="post" class="mb-3" onsubmit="showLoading()">
                <div class="input-group mb-3">
                    <input type="text" name="user_input" class="form-control" placeholder="Enter something..." required>
                    <button class="btn btn-primary" type="submit">Submit</button>
                </div>
                <a href="/" class="btn btn-secondary mt-3">Restart Conversation</a>
                <a href="/dashboard" class="btn btn-secondary mt-3">End Chat and View Dashboard</a>
            </form>
            <div id="loading" class="spinner-border text-primary" role="status" style="display:none;">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
        {% if qa_list %}
            <h3 class="mb-3">Questions and Answers:</h3>
            <div class="scrollable-list">
                <ul class="list-group">
                    {% for qa in qa_list %}
                        <li class="list-group-item">
                            <strong>Q:</strong> {{ qa.question }}<br>
                            <strong>A:</strong> {{ qa.answer }}
                        </li>
                    {% endfor %}
                </ul>
            </div>
        {% endif %}
    </div>
    <script>
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h2 class="mb-4">Dashboard</h2>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Mental Health</th>
                    <th>Physical Health</th>
                    <th>Knowledge</th>
                    <th>Preventive</th>
                    <th>Health Seeking</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{ analysis.mental_health }}</td>
                    <td>{{ analysis.physical_health }}</td>
                    <td>{{ analysis.knowledge }}</td>
                    <td>{{ analysis.preventive }}</td>
                    <td>{{ analysis.health_seeking }}</td>
                </tr>
            </tbody>
        </table>
        <a href="/" class="btn btn-primary">Back to Form</a>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""