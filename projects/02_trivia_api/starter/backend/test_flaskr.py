import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    

    def setUp(self):
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_USER = os.getenv('DB_USER')
        self.DB_PASS = os.getenv('DB_PASS')
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = self.DB_NAME
        self.database_path = "postgres://{}/{}".format(self.DB_USER+':'+self.DB_PASS+'@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.newQuestion = {
            'id': 20,
            'question' : 'When is the International Yoga Day Celebrated ',
            'answer': '21 June',
            'category': 1,
            'difficulty': 2
        }
        self.newQuestion1 = {
            'id': 20,
            'question' : 'When is the International Yoga Day Celebrated ',
            'answer': '21 June',
            'category': 'Science',
            'difficulty': 2
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_default_route(self):
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)

    def test_add_question(self):
        res = self.client().post('/questions', json=self.newQuestion)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertTrue(len(data['categories']))

    def test_422_get_categories(self):
        res = self.client().post('/categories')
        self.assertTrue(res.status_code, 422)


    def test_404_get_questions(self):
        res = self.client().get('/questions', query_string={'page':1000})
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data['Error Message'], 'Not Found')

    def test_search_Question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'which'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))

    def test_422_search_Question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'FindTheTerm'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['Error Message'], 'Unprocessable')

    

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
    
    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_400_delete_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['Error Message'],'Bad Request')
    
    def test_422_quizzes(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['Error Message'], 'Unprocessable')

    def test_422_add_question(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['Error Message'], 'Unprocessable')

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_422_get_questions_by_category(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['Error Message'], 'Unprocessable')






# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()