import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,PATCH,DELETE,OPTIONS"
        )
        response.headers.add(
            "Access-Control-Allow-Credentials", "true"
        )

        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def categories():
        all_categories = Category.query.all()
        all_categories = {category.id: category.type for
                          category in all_categories}

        return jsonify(
            {"success": True,
             "categories": all_categories}
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)
        current_category = Category.query.get(1)
        current_category = current_category.format()["type"]
        question_categories = Category.query.all()
        question_categories = {category.id: category.type for
                               category in question_categories}

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "categories": question_categories,
                "current_category": current_category
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question:
            try:
                question.delete()
            except:
                abort(500)
            else:
                return jsonify({
                    "success": True,
                    "question_id": question_id
                }), 200
        else:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def add_questions():
        data = request.get_json()
        for i in data.values():
            if i == "":
                abort(422)
        question = data.get('question', None)
        answer = data.get('answer', None)
        difficulty = data.get('difficulty', None)
        category = data.get('category', None)
        new_question = Question(
            question=question,
            answer=answer,
            category=category,
            difficulty=difficulty
        )
        try:
            new_question.insert()
        except Exception as e:
            print(e)
            abort(500)

        return jsonify({
            "success": True
        }), 200

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/question", methods=["POST"])
    def search_questions():
        data = request.get_json()

        search_term = data.get("searchTerm", None)

        search_result = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()
        current_search = paginate_questions(request, search_result)
        current_category = Category.query.get(1)
        current_category = current_category.format()["type"]

        return jsonify({
            "success": True,
            "questions": current_search,
            "total_questions": len(search_result),
            "current_category": current_category
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<cat_id>/questions")
    def questions_by_categories(cat_id):
        current_category = Category.query.get(cat_id)
        if current_category:
            current_category = current_category.format()["type"]
            questions = Question.query.filter_by(category=cat_id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                "questions": current_questions,
                "total_questions": len(questions),
                "current_category": current_category,
                "success": True
            })
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_quiz():
        data = request.get_json()
        previous_question = data.get("previous_questions")
        quiz_category = data.get("quiz_category")

        if quiz_category["id"] == 0:  # all categories
            all_questions = Question.query.all()
        else:
            # other categories
            all_questions = Question.query.filter_by(
                category=quiz_category["id"]).all()

            if not all_questions:

                abort(404)

        question_list = [q.format() for q in all_questions
                         if q.id not in previous_question]

        if question_list == []:
            return jsonify({
                "success": True
            })

        else:

            question = random.choice(question_list) #generate a random question

            return jsonify({
                "success": True,
                "question": question
            })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404,
                     "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422,
                     "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400,
                        "message": "bad request"}), 400

    @app.errorhandler(500)
    def internal_error(error):
        return (
            jsonify({"success": False, "error": 500,
                     "message": "internal server error"}),
            500,
        )

    return app

