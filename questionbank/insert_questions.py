import sys
import os

from __init__ import path
path()

from connection.db_connection import get_db_connection

import mysql.connector 
from mysql.connector import errorcode

# Sample data
questions = [
    {
        'question_id': 1,
        'title': 'Palindrome Number',
        'description': 'Given an integer x, return true if x is a palindrome, and false otherwise.',
        'difficulty': 'Easy'
    },
    {
        'question_id': 2,
        'title': 'Reverse Integer',
        'description': 'Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-231, 231 - 1], then return 0.',
        'difficulty': 'Medium'
    },
    {
        'question_id': 3,
        'title': 'Valid Parentheses',
        'description': 'Given a string containing just the characters \'(\', \')\', \'{\', \'}\', \'[\' and \']\', determine if the input string is valid.',
        'difficulty': 'Easy'
    },
    {
        'question_id': 4,
        'title': 'Longest Valid Parentheses',
        'description': 'Given a string containing just the characters \'(\' and \')\', find the length of the longest valid (well-formed) parentheses substring.',
        'difficulty': 'Hard'
    },
    {
        'question_id': 5,
        'title': 'Container With Most Water',
        'description': 'Given n non-negative integers a1, a2, ..., an, where each represents a point at coordinate (i, ai). Find two lines, which together with x-axis forms a container, such that the container contains the most water.',
        'difficulty': 'Hard'
    }
]

test_cases = [
    {
        'test_case_id': 1,
        'question_id': 1,
        'input': '121',
        'expected_output': 'true'
    },
    {
        'test_case_id': 2,
        'question_id': 1,
        'input': '-121',
        'expected_output': 'false'
    },
    {
        'test_case_id': 3,
        'question_id': 1,
        'input': '10',
        'expected_output': 'false'
    },
    {
        'test_case_id': 4,
        'question_id': 2,
        'input': '123',
        'expected_output': '321'
    },
    {
        'test_case_id': 5,
        'question_id': 2,
        'input': '-123',
        'expected_output': '-321'
    },
    {
        'test_case_id': 6,
        'question_id': 2,
        'input': '1534236469',
        'expected_output': '0'
    },
    {
        'test_case_id': 7,
        'question_id': 3,
        'input': '"()"',
        'expected_output': 'true'
    },
    {
        'test_case_id': 8,
        'question_id': 3,
        'input': '"()[]{}"',
        'expected_output': 'true'
    },
    {
        'test_case_id': 9,
        'question_id': 3,
        'input': '"(]"',
        'expected_output': 'false'
    },
    {
        'test_case_id': 10,
        'question_id': 4,
        'input': '"(()"',
        'expected_output': '2'
    },
    {
        'test_case_id': 11,
        'question_id': 4,
        'input': '")()())"',
        'expected_output': '4'
    },
    {
        'test_case_id': 12,
        'question_id': 4,
        'input': '""',
        'expected_output': '0'
    },
    {
        'test_case_id': 13,
        'question_id': 5,
        'input': '[1,8,6,2,5,4,8,3,7]',
        'expected_output': '49'
    },
    {
        'test_case_id': 14,
        'question_id': 5,
        'input': '[1,1]',
        'expected_output': '1'
    },
    {
        'test_case_id': 15,
        'question_id': 5,
        'input': '[4,3,2,1,4]',
        'expected_output': '16'
    }
]

def create_tables(cursor):
    create_questions_table = (
        "CREATE TABLE IF NOT EXISTS questions ("
        " question_id INT PRIMARY KEY,"
        " title VARCHAR(255),"
        " description TEXT,"
        " difficulty VARCHAR(50)"
        ") ENGINE=InnoDB")

    create_test_cases_table = (
        "CREATE TABLE IF NOT EXISTS test_cases ("
        " test_case_id INT PRIMARY KEY,"
        " question_id INT,"
        " input TEXT,"
        " expected_output TEXT,"
        " FOREIGN KEY (question_id) REFERENCES questions(question_id)"
        ") ENGINE=InnoDB")

    cursor.execute(create_questions_table)
    cursor.execute(create_test_cases_table)

def insert_data(cursor):
    # Using ON DUPLICATE KEY UPDATE to handle duplicates
    add_question = (
        "INSERT INTO questions (question_id, title, description, difficulty) "
        "VALUES (%s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE "
        "title=VALUES(title), description=VALUES(description), difficulty=VALUES(difficulty)"
    )
    for question in questions:
        cursor.execute(add_question, (question['question_id'], question['title'], question['description'], question['difficulty']))

    add_test_case = (
        "INSERT INTO test_cases (test_case_id, question_id, input, expected_output) "
        "VALUES (%s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE "
        "input=VALUES(input), expected_output=VALUES(expected_output)"
    )
    for test_case in test_cases:
        cursor.execute(add_test_case, (test_case['test_case_id'], test_case['question_id'], test_case['input'], test_case['expected_output']))

def main():
    # Get the database connection and database name
    cnx, db_name = get_db_connection()
    
    if cnx is None or db_name is None:
        print("Connection failed.")
        exit(1)

    try:
        cursor = cnx.cursor()
        create_tables(cursor)
        insert_data(cursor)
        cnx.commit()
        print("Data inserted successfully.")
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
