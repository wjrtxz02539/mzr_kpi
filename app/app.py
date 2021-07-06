import os
from flask import Flask
from .api import api_blueprint, APICounter
from .web import web

pwd = os.path.dirname(__file__)

app = Flask('BiliCommentAnalyzer', template_folder=os.path.join(pwd, 'templates'),
            static_folder=os.path.join(pwd, 'static'))
app.register_blueprint(api_blueprint)
app.register_blueprint(web)

app.before_request_funcs = {None: [APICounter.count]}
