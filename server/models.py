from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from config import db, bcrypt
from sqlalchemy import CheckConstraint
from sqlalchemy.exc import IntegrityError

class User(db.Model, SerializerMixin):

    __tablename__ = 'users'

    serialize_rules=('-recipes.user',)

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String, unique=True, nullable = False)
    image_url=db.Column(db.String)
    bio=db.Column(db.String)
    _password_hash=db.Column(db.String)

    recipes = db.relationship("Recipe", backref="user")


    @hybrid_property
    def password_hash(self):
        raise AttributeError("cannot access")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint("length(instructions) >= 50"),
    )

    
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String, nullable=False)
    instructions=db.Column(db.String, nullable = False)
    minutes_to_complete=db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))