#!/usr/bin/env python
'''
  This demo application demonstrates the functionality of the safrs documented REST API
  After installing safrs with pip, you can run this app standalone:
  $ python3 demo_relationship.py [Listener-IP]

  This will run the example on http://Listener-Ip:5000

  - A database is created and a user is added
  - A rest api is available
  - swagger documentation is generated

  This is a minimal example, you'll probably want to use demo_relationship_ext.py instead!!!
'''
import sys
import logging
import builtins
import datetime
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from safrs import SAFRSBase, jsonapi_rpc
from safrs import SAFRSJSONEncoder, Api
db = SQLAlchemy()

# Example sqla database object
class User(SAFRSBase, db.Model):
    '''
        description: User description
    '''
    __tablename__ = 'Users'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, default='')
    email = db.Column(db.String, default='')
    dob = db.Column(db.Date, default='1970-01-01')
    created = db.Column(db.DateTime, default=datetime.datetime.now())
    books = db.relationship('Book', back_populates="user", lazy='dynamic')

    # Following method is exposed through the REST API
    # This means it can be invoked with a HTTP POST
    @classmethod
    @jsonapi_rpc(http_methods = ['POST','GET'])
    def send_mail(self, **args):
        '''
        description : Send an email
        args:
            email:
                type : string
                example : test email
        '''
        return {'result' : args}

class Book(SAFRSBase, db.Model):
    '''
        description: Book description
    '''
    __tablename__ = 'Books'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, default='')
    user_id = db.Column(db.String, db.ForeignKey('Users.id'))
    user = db.relationship('User', back_populates='books')


if __name__ == '__main__':
    HOST = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    PORT = 5000
    app = Flask('SAFRS Demo Application')
    app.config.update(SQLALCHEMY_DATABASE_URI='sqlite://', DEBUG=True)
    db.init_app(app)
    db.app = app
    # Create the database
    db.create_all()
    API_PREFIX = ''
    
    with app.app_context():
        # Create a user and a book and add the book to the user.books relationship
        user = User(name='thomas', email='em@il')
        book = Book(name='test_book')
        user.books.append(book)
        api = Api(app, api_spec_url=API_PREFIX + '/swagger', host='{}:{}'.format(HOST, PORT))
        # Expose the database objects as REST API endpoints
        api.expose_object(User)
        api.expose_object(Book)
        # Set the JSON encoder used for object to json marshalling
        app.json_encoder = SAFRSJSONEncoder
        # Register the API at /api/docs
        swaggerui_blueprint = get_swaggerui_blueprint(API_PREFIX, API_PREFIX + '/swagger.json')
        app.register_blueprint(swaggerui_blueprint, url_prefix=API_PREFIX)
        print('Starting API: http://{}:{}{}'.format(HOST, PORT, API_PREFIX))
        app.run(host=HOST, port=PORT)