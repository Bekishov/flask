from peewee import *
import datetime
from flask_login import UserMixin

db = PostgresqlDatabase(
    'flaskm_db',
    host = 'localhost',
    port = 5432,
    user = 'flaskm_user',
    password = 'qwe123'
)
db.connect()

class BaseModel(Model):
    class Meta:
        database = db

class MyUser(BaseModel, UserMixin):
    email = CharField(max_length=225, null = False, unique = True)
    name = CharField(max_length=225, null = False)
    second_name = CharField(max_length=225, null = False)
    password = CharField(max_length=225, null = False)
    age = IntegerField()

    def __repr__(self):
        return self.email
    

class Post(BaseModel):
    author = ForeignKeyField(MyUser, on_delete='CASCADE')
    title = CharField(max_length=225, null = False)
    description = TextField()
    date = DateTimeField(default=datetime.datetime.now)
   


    def __repr__(self):
        return self.title
    
class Resume(BaseModel):
    name = CharField(max_length=225, null = True)
    address = CharField(max_length=225, null = False)
    phone = CharField(max_length=225, null = False)
    email = CharField(max_length=225, null = False, unique = True)
    education = TextField()
    experience = TextField()

    def __repr__(self):
        return self.name


    
db.create_tables([MyUser,Post,Resume])
