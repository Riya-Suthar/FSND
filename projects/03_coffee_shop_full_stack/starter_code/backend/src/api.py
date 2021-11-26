import os
import re
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure

'''
@app.route('/drinks',methods=['GET'])
def get_drinks_short():
    #return 'not implemented yet'
    try:
        drinks = Drink.query.all()
        drink = [d.short() for d in drinks]
        print(drink)
        if drink is None:
            drink = []
        return jsonify(
        {
        'success': True,
        'drinks': [d.short() for d in drinks]}), 200
    except Exception as e:
        print(e)
        return jsonify({
            'error code': 404,
            'reason': 'not found'
        })
    # drinks = Drink.query.all()

    # return jsonify({
    #     'success': True,
    #     'drinks': [drink.short() for drink in drinks]
    # }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_long(payload):
    # return 'not implemented yet'
    try:
        drinks = Drink.query.all()
        drink = [d.long() for d in drinks]
        print(drink)
        return jsonify(
        {
        'success': True,
        'drinks': drink}), 200
    except AuthError as e:
        abort(401)
    except Exception as e:
        if(e['code']=='authorization_header_missing'):
            abort(401)
        abort(404)
        # return jsonify({
        #     'error code': 404,
        #     'reason': 'not found'
        # })
    finally:
        abort(401)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
        })
'''
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    # # return 'not implemented yet'
    # try:
    #     print(request)
    #     body = request.get_json()
    #     # json_data = json.loads(body)
    #     print(body)
    #     # drink_id=int(body.get("id"))
    #     drink_title = body.get("title")
    #     drink_r = body.get("recipe")
    #     # drink_rec = json.dumps(drink_r)

        
    #     # print(type(drink_rec))
    #     # print(drink_title)
    #     # print(drink_rec)
    #     # print(type(drink_rec)) 
    #     drink = Drink(title=drink_title, recipe=json.dumps(drink_r))
    #     drink.insert()
    #     # print(drink)
    #     return jsonify(
    #     {
    #     'success': True,
    #     'drinks': drink.long()}), 200
    # except Exception as e:
    #     return jsonify({
    #         'error code': 404,
    #         'reason': 'not found'}),404
     # Get the body
    req = request.get_json()
    try:
        # create new Drink
        drink = Drink()
        drink.title = req['title']
        # convert recipe to String
        drink.recipe = json.dumps(req['recipe'])
        # insert the new Drink
        drink.insert()

    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200




'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt,id):
    # # id = request.args.get('id',None)
    # print("********************************")
    # print(id)
    # if id is None:
    #     abort(422)
    
    # if(id>=1):
        
    #         drink = Drink.query.filter(Drink.id==id).one_or_none()
    #         if drink is None:
    #             abort(404)
    #         data = request.get_json()
    #         drink.title = data.get('title')
    #         drink.recipe = data.get('recipe')
    #         drink.update()
    #         return jsonify({
    #             'success': True,
    #             'drinks':drink
    #         }), 200
      
    # else:
    #     abort(404)
    req = request.get_json()

    # Get the drink with requested Id
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    # if no drink with given id abort
    if not drink:
        abort(404)

    try:

        req_title = req.get('title')
        req_recipe = req.get('recipe')

        # check if the title is the one is updated
        if req_title:
            drink.title = req_title

        # check if the recipe is the one is updated
        if req_recipe:
            drink.recipe = json.dumps(req['recipe'])

        # update the drink
        drink.update()
    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt,id):
    try:
        # id = request.args.get('id',None)
        if id is None:
            abort(404)
        drink = Drink.query.filter(Drink.id==id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success':True,
            'delete':id
        }), 200
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422



'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    print(error)
    return jsonify({
        "success":False,
        "error":error.status_code,
        "message":error.error['description']
    }), error.status_code





'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unauthorized(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(403)
def bad_request(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 403,
        "message": 'Forbidden'
    }), 403


@app.errorhandler(405)
def method_not_allowed(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405