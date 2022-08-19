import os
import unittest
import json
from unittest import result
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
                                'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Who let the dogs",
                             "answer": "Who who who who",
                             "category": 2,
                             "difficulty": 5}

        self.fail_question = {"question": "",
                              "answer": "",
                              "category": 2,
                              "difficulty": 5

                              }

        self.search_term = {"searchTerm": "who"}
        self.quiz_parameter_all = {
            "previous_questions": [],
            "quiz_category": {
                "type": "click",
                "id": 0
            }
        }

        self.quiz_parameter_others = {
            "previous_question": [8, 9],
            "quiz_category": {
                "type": "click",
                "id": 1
            }
        }

        self.quiz_fail = {
            "previous_question": [10, 11],
            "quiz_category": {
                "type": "click",
                "id": 500
            }
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation
    and for expected errors.
    """

    def test_get_paginated_questions(self):
        results = self.client().get('/questions')
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['questions']))
        self.assertTrue((data['current_category']))

    def test_404_sent_requesting_after_valid_page(self):
        results = self.client().get('/questions?page=1000')
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_question_category(self):
        results = self.client().get('/categories/2/questions')
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue((data['current_category']))

    def test_delete_question_success(self):
        results = self.client().get('/categories/2/questions')
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue((data['current_category']))

    def test_404_sent_requesting_invalid_category(self):
        results = self.client().get('/category/115/questions?page=1000')
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        results = self.client().get("/categories")
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_404_requesting_categories(self):
        results = self.client().get("/categories/500")
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_404_if_question_does_not_exist(self):
        results = self.client().delete("/questions/1000")
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_create_new_question(self):
        results = self.client().post("/questions", json=self.new_question)
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_422_if_question_creation_fails(self):
        results = self.client().post("/questions", json={
            'difficulty': "one"})
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_question(self):
        results = self.client().post("/question/search", json=self.search_term)
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue((data['current_category']))

    def test_get_quiz(self):
        results = self.client().post("/quizzes", json=self.quiz_parameter_all)
        data = json.loads(results.data)
        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_search_question_failure(self):
        results = self.client().post("/quizzes", json=self.quiz_fail)
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"],
                         "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
