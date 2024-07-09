import os
import sys
import click

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate



# 设置数据库 URI
WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))

login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = 'login'

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from src import models

@app.before_first_request
def create_tables():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    from src.models import User
    user = User.query.get(int(user_id))
    return user

@app.context_processor
def inject_user():  # 函数名可以随意修改
    from src.models import User
    user = User.query.first()
    return dict(user=user)

from src import views, errors, commands
