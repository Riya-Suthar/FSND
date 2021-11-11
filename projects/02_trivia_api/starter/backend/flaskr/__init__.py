import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.operators import exists

from sqlalchemy.sql.selectable import CTE
from sqlalchemy.sql.sqltypes import String

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*" : { "origins" : "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def afterRequest(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def getCategories():
    allCategories = Category.query.all()
    categories = {}
    for cat in allCategories:
      categories[cat.id] = cat.type

    return jsonify({"categories" : categories})


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def getQuestions():
    page = request.args.get('page', 1, type=int)
    currentCategory = request.args.get('currentCategory', 'Art' , type=String)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.all()
    questionsOnPage = [question.format() for question in questions]
    categories = Category.query.all()
    cats = {}
    for category in categories:
      cats[category.id] = category.type
    
    return jsonify ({
      'success': True,
      'questions': questionsOnPage[start:end],
      'totalQuestions': len(questionsOnPage),
      'categories': cats,
      'current_category': currentCategory
    })


      


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def deleteQuestion(id):
    question = Question.query.filter(Question.id==id).one_or_none()
    page = request.args.get("page",1,type=int)
    start = (page -1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    if question is None:
      abort(404)
    
    question.delete()
    totalQuestions = Question.query.all()
    questions = [question.format() for question in totalQuestions]
    questions = questions[start:end]
    return jsonify({
      'success':True,
      'questions' : questions,
      'totalQuestion' : len(totalQuestions)


    })



  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def addQuestion():
    reqBody = request.get_json()
    question = reqBody.get("question", None)
    answer = reqBody.get("answer", None)
    difficulty = reqBody.get("difficulty", None)
    category = reqBody.get("category", None)

    question = Question(question=question,answer=answer,difficulty=difficulty,category=category)
    question.insert()

    page = request.args.get('page', 1 , type=int)
    start = (page -1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = Question.query.all()
    question = [q.format() for q in questions[start:end]]

    return jsonify({
      'success':True,
      'questions':question,
      'totalQuestions':len(questions)
    })




  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods = ['POST'])
  def searchQuestion():
    reqBody = request.get_json()
    term = reqBody.get("searchTerm", None)
    currentCategory = reqBody.get("currentCategory", None)
    # body = request.get_json()
    # searchTerm = body.get('searchTerm')
    print(term)
    question = Question.query.all()
    page = request.args.get('page',1,type=int)
    start = (page - 1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = []
    for q in question:
      print(str(q.question))
      if(q.question!=None):
        if(str(term) in str(q.question)):
          print("found ==================")
          questions.append(q.format())

    total_questions = questions[start:end]

   
    return jsonify({
      'success':True,
      'questions':total_questions,
      'totalQuestions':len(questions),
      'current_category': currentCategory
      
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<int:id>/questions", methods=['GET'])
  def getQuestionsByCategory(id):
    page = request.args.get('page', 1)
    categoryName = Category.query.with_entities(Category.type).filter(Category.id == id).all()
    for c in categoryName:
      name = c.type
    # print(name)
    start = (page - 1 )* QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.filter(Question.category==id)
    question = [question.format() for question in questions]
    return jsonify({
      'questions': question[start:end],
      'total_questions': len(question),
      'current_category': name
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def playQuiz():
    body = request.get_json()
    category = body.get('quiz_category')
    previous_questions = body.get('previous_questions')
    questions = Question.query.filter(Question.category==category.get('id')).all()
    for q in questions:
      if(q.id not in previous_questions):
        previous_questions.append(q.id)
        question = q.format()
       
        break;
    return jsonify({
      'success':True,
      'question': question
    })



  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 

  '''
  @app.errorhandler(404)
  def notFound(error):
    return jsonify({"Error Message" : "Not Found"}),404

  @app.errorhandler(422)
  def notFound(error):
    return jsonify({"Error Message" : "Unprocessable"}),422

  @app.errorhandler(400)
  def notFound(error):
    return jsonify({"Error Message" : "Bad Request"}),400
  
  @app.errorhandler(500)
  def notFound(error):
    return jsonify({"Error Message" : "OOps Something Went Wrong!"}),500

  
  
  return app

    