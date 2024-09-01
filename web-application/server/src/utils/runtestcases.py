import sys
import json
import re
import mysql.connector

def connect_to_db():
    try:
        return mysql.connector.connect(
            host='mysql', # You can also use '172.18.0.2' - The ip of your mysql container
            user='root',
            password='9084Mysql#',
            database='doodle',
            port=3306
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}", file=sys.stderr)
        sys.exit(1)

def fetch_test_cases(db_connection, question_id):
    cursor = db_connection.cursor(dictionary=True)
    query = "SELECT * FROM test_cases WHERE question_id = %s"
    cursor.execute(query, (question_id,))
    test_cases = cursor.fetchall()
    cursor.close()
    return test_cases

def run_tests(question_id, code, test_cases):
    results = []

    print('Running tests for question ID:', question_id, file=sys.stderr)
    print('Code:', code, file=sys.stderr)
    print('Test cases:', test_cases, file=sys.stderr)

    match = re.search(r'def (\w+)\(', code)
    if not match:
        return [{"test_case_id": test["test_case_id"], "passed": False, "error": "Invalid function definition"} for test in test_cases]

    func_name = match.group(1)
    local_env = {}
    try:
        exec(code, {}, local_env)
    except Exception as e:
        return [{"test_case_id": test["test_case_id"], "passed": False, "error": str(e)} for test in test_cases]

    for test in test_cases:
        try:
            input_data = json.loads(f'[{test["input"]}]')
            expected_output = json.loads(test['expected_output'])
            result = eval(f'local_env["{func_name}"](*input_data)')
            results.append({
                "test_case_id": test['test_case_id'],
                "passed": result == expected_output,
                "error": None
            })
        except Exception as e:
            results.append({
                "test_case_id": test['test_case_id'],
                "passed": False,
                "error": str(e)
            })
    return results

if __name__ == "__main__":
    question_id = sys.argv[1]
    code = sys.argv[2].replace('\\n', '\n')
    db_connection = connect_to_db()
    test_cases = fetch_test_cases(db_connection, question_id)
    results = run_tests(question_id, code, test_cases)
    db_connection.close()

    print(json.dumps(results))