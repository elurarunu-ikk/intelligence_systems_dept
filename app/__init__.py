import os
from flask import Flask
from .extensions import db, login_manager,migrate
from flask_admin import Admin
from .models import User
from .blueprints.public.routes import public_bp
from .blueprints.auth.routes import auth_bp
from .admin_views import setup_admin,SecureAdminIndexView
from .config import Config

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ✅ ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_object(Config())

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Flask-Admin (secure index)
    admin = Admin(
        app,
        name="Department CMS",
        template_mode="bootstrap4",
        url="/admin",
        index_view=SecureAdminIndexView(url="/admin")
    )
    from flask_admin.menu import MenuLink
    admin.add_link(MenuLink(name="Back to Website", url="/"))

    setup_admin(admin)

    with app.app_context():
        db.create_all()
        _seed_admin_user(app)

      #  from .seed_data import seed_if_empty
      #  seed_if_empty(app)

    return app


def _seed_admin_user(app: Flask):
    email = app.config.get("ADMIN_EMAIL", "admin@saveetha.edu.in")
    password = app.config.get("ADMIN_PASSWORD", "ChangeMe@123")

    # ✅ Seed only if that admin email is missing
    exists = User.query.filter_by(email=email).first()
    if exists:
        return

    user = User(email=email, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

