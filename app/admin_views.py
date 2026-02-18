import os
from flask import current_app,redirect, url_for, request
from flask_login import current_user
from flask_admin import AdminIndexView,form
from app.models import HeroSlide
from flask_admin.contrib.sqla import ModelView
from wtforms.validators import DataRequired
from flask_admin.form.upload import ImageUploadField
from werkzeug.utils import secure_filename
from markupsafe import Markup
from wtforms.validators import DataRequired

from .extensions import db
from .models import (
    User, SiteSettings, Page, Program, Faculty,
    News, Event, Achievement, FundedProject,
    MoU, PlacementStat, Newsletter, Enquiry, 
    GalleryAlbum, GalleryImage,Alumni,HeroSlide
)

class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, "is_admin", False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))

class SecureModelView(ModelView):
    page_size = 25
    can_export = True
    create_modal = False
    edit_modal = False
    details_modal = False

    form_widget_args = {}
    form_widget_args ={}

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, "is_admin", False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))

def setup_admin(admin):
    admin.add_view(SecureModelView(SiteSettings, db.session, category="Settings")) 
    admin.add_view(HeroSlideAdmin(HeroSlide, db.session, category="Content"))
   # admin.add_view(SiteSettingsAdmin(SiteSettings, db.session, category="Settings")) # --Added 24JAn2026
    admin.add_view(SecureModelView(Page, db.session, category="Content"))
  #  admin.add_view(SecureModelView(Program, db.session, category="Academics"))
    admin.add_view(SecureModelView(Faculty, db.session, category="Faculty"))

    admin.add_view(SecureModelView(News, db.session, category="News & Media"))
    admin.add_view(SecureModelView(Event, db.session, category="News & Media"))
   # admin.add_view(SecureModelView(Newsletter, db.session, category="News & Media"))

    admin.add_view(SecureModelView(Achievement, db.session, category="Highlights"))
    admin.add_view(SecureModelView(FundedProject, db.session, category="Research"))

    admin.add_view(SecureModelView(MoU, db.session, category="Industry"))
    admin.add_view(SecureModelView(PlacementStat, db.session, category="Industry"))

    admin.add_view(SecureModelView(Enquiry, db.session, category="Enquiries"))
    admin.add_view(SecureModelView(User, db.session, category="Access"))

   # admin.add_view(SecureModelView(GalleryAlbum, db.session, category="Media"))
   # admin.add_view(GalleryImageView(GalleryImage, db.session, category="Media"))
 
   # admin.add_view(SecureModelView(Alumni, db.session, category="People"))
    admin.add_view(GalleryAlbumView(GalleryAlbum, db.session, category="Media"))
    admin.add_view(GalleryImageView(GalleryImage, db.session, category="Media"))

# --- HeroSlide admin with image upload ---
class HeroSlideAdmin(SecureModelView):
    form_extra_fields = {
        "image_url": ImageUploadField(
            "Slide Image",
            base_path=lambda: os.path.join(current_app.root_path, "static", "images", "headers"),
            url_relative_path="images/headers/",
            namegen=lambda obj, file_data: secure_filename(file_data.filename),
            allowed_extensions=("jpg", "jpeg", "png", "webp"),
        )
    }

    def on_model_change(self, form, model, is_created):
        if model.image_url:
            v = str(model.image_url).strip()

            # Case 1: already a full static path
            if v.startswith("/static/"):
                model.image_url = v

            # Case 2: field returns only filename like 'about.jpg' (no slashes)
            elif "/" not in v and "\\" not in v:
                model.image_url = f"/static/images/headers/{v}"

            # Case 3: field returns relative path like 'images/headers/about.jpg'
            else:
                v = v.replace("\\", "/")
                model.image_url = "/static/" + v.lstrip("/")

        super().on_model_change(form, model, is_created)

    
   
class FacultyView(SecureModelView):
    form_columns = (
        "name","designation","display_order","specialization",
        "email","phone","photo_url","bio_html","is_published",
    )

    # Upload into: app/static/images/faculty/
    form_extra_fields = {
        "photo_url": ImageUploadField(
            "Faculty Photo",
            base_path=lambda: os.path.join(current_app.root_path, "static", "images", "faculty"),
            url_relative_path="images/faculty/",
            namegen=lambda obj, file_data: secure_filename(file_data.filename),
            allowed_extensions=("jpg", "jpeg", "png", "webp"),
        )
    }

    def on_model_change(self, form, model, is_created):
        if model.photo_url:
            v = str(model.photo_url).strip().replace("\\", "/")

            # If filename only
            if "/" not in v:
                v = f"images/faculty/{v}"

            # Ensure /static prefix
            if not v.startswith("/static/"):
                v = "/static/" + v.lstrip("/")

            model.photo_url = v

        super().on_model_change(form, model, is_created)

class GalleryAlbumView(SecureModelView):
    column_list = ("display_order", "title", "category", "year", "is_published", "cover_image_url")
    column_sortable_list = ("display_order", "year", "title")
    column_default_sort = ("display_order", True)

    form_columns = ("display_order", "title", "category", "year", "is_published", "cover_image_url")

    # ✅ cover upload
    form_extra_fields = {
        "cover_image_url": ImageUploadField(
            "Album Cover",
            base_path=lambda: os.path.join(current_app.root_path, "static", "images", "gallery"),
            url_relative_path="images/gallery/",
            namegen=lambda obj, file_data: secure_filename(file_data.filename),
            allowed_extensions=("jpg", "jpeg", "png", "webp"),
        )
    }

    def _cover_thumb(self, context, model, name):
        if not model.cover_image_url:
            return ""
        return Markup(f'<img src="{model.cover_image_url}" style="height:40px;border-radius:6px;">')

    column_formatters = {"cover_image_url": _cover_thumb}


class GalleryImageView(SecureModelView):
    column_list = ("display_order", "album", "image_url", "caption")
    column_sortable_list = ("display_order", "album", "caption")
    column_default_sort = ("display_order", True)

    # keep as text input (manual path) "jpg", "jpeg", "png", "webp"
    form_columns = ("album", "display_order", "image_url", "caption")

    # ✅ image upload (browse)
   #    form_extra_fields = {
   #       "image_url": ImageUploadField(
   #           "Gallery Image",
    #        base_path=lambda: os.path.join(current_app.root_path, "static", "images", "gallery"),
     #       url_relative_path="images/gallery/",
      #      namegen=lambda obj, file_data: secure_filename(file_data.filename),
       #     allowed_extensions=("jpg", "jpeg", "png", "webp"),) }

    form_args = {
        "album": {"get_label": "title"},
        "image_url": {"validators": [DataRequired()]},  # require path if upload image, comment the line
    }

    form_widget_args = {
    "image_url": {
        "placeholder": "/static/images/gallery/yourfile.webp"
    }
}


    def _img_thumb(self, context, model, name):
        if not model.image_url:
            return ""
        return Markup(
            f'<img src="{model.image_url}" '
            f'style="height:40px;width:auto;border-radius:6px;object-fit:cover;">'
        )

    column_formatters = {"image_url": _img_thumb}


   
class PageView(SecureModelView):
    form_columns = (
        "title",
        "slug",
        "header_image_url",
        "header_subtitle",
        "body_html",
        "is_published",
        "show_in_menu",
    )

    
from flask_admin.form import rules

class SiteSettingsAdmin(SecureModelView):
    can_create = False
    can_delete = False

    form_edit_rules = (
        rules.Header("Branding"),
        "dept_name","tagline",

        rules.Header("Home Banner"),
        "home_hero_default_image_url",
        "home_hero_interval_ms",

        rules.Header("Section Banners"),
        "banner_faculty",
        "banner_news",
        "banner_events",

        rules.Header("Contact"),
        "enquiry_email","phone","address",
    )

class NewsView(SecureModelView):
    def on_model_change(self, form, model, is_created):
        if model.cover_image_url:
            v = str(model.cover_image_url).strip().replace("\\", "/")
            if v and not v.startswith("/"):
                v = "/" + v
            model.cover_image_url = v
        super().on_model_change(form, model, is_created)


