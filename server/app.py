#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()

        if not json.get('username'):
            return {'message':'invalid username'}, 422

        user = User(
            username=json.get('username'),
            image_url=json.get('image_url'),
            bio=json.get('bio'),
        )
        user.password_hash=json.get('password')

        if not user:
            return {'message':'invalid user info'}, 422
   
        db.session.add(user)
        db.session.commit()
        
        session['user_id']=user.id
        return user.to_dict(), 201

class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
       
        if user:
            return user.to_dict(), 200
        else:
            return {}, 401

class Login(Resource):
    def post(self):
        
        user_info = request.get_json()

        user = User.query.filter(User.username == user_info.get('username')).first()
        
        if user and user.authenticate(user_info.get('password')):
            
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {}, 401

class Logout(Resource):
    def delete(self):

        session['user_id'] = None
        
        return {}, 401

class RecipeIndex(Resource):
    def get(self):
        if session['user_id']:
            recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
            return recipes, 200
        else:
            return {'message':'unauthorized'}, 401


    def post(self):
        if session['user_id']:
            data = request.get_json()

            recipe = Recipe(
                title=data['title'],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=session['user_id']
            )

            try:
                db.session.add(recipe)
                db.session.commit()
            except:
                return {'message':'invalid recipe'}, 422

            return recipe.to_dict(), 201
            
        else:
            return {'message':'unauthorized'}, 401
    



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)