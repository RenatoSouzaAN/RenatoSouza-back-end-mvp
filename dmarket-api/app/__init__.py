# from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flasgger import Swagger
# from flask_cors import CORS

# db = SQLAlchemy()
# migrate = Migrate()
# swagger = Swagger()

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object('app.config.Config')

#     db.init_app(app)
#     migrate.init_app(app, db)
#     swagger.init_app(app)

#     CORS(app)

#     with app.app_context():
#         from . import routes
#         return app
