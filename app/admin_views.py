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
   # admin.add_view(SecureModelView(Page, db.session, category="Content"))
    admin.add_view(PageView(Page, db.session, category="Content"))
  #  admin.add_view(SecureModelView(Program, db.session, category="Academics"))
    #admin.add_view(SecureModelView(Faculty, db.session, category="Faculty"))
    admin.add_view(FacultyView(Faculty, db.session, category="Faculty"))

    # admin.add_view(SecureModelView(News, db.session, category="News & Media"))
    admin.add_view(NewsView(News, db.session, category="News & Media"))
    # admin.add_view(SecureModelView(Event, db.session, category="News & Media"))
    admin.add_view(EventView(Event, db.session, category="News & Media"))
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

    column_list = ("order","title", "image_url", "is_active")
    column_sortable_list = ("order", "title", "is_active")
    column_default_sort = ("order", True)

    form_columns = ("order", "title", "subtitle", "image_url", "cta_text", "cta_url", "is_active")


	#form_extra_fields = {
	#		"image_url": ImageUploadField(
	#			"Slide Image",
	#			base_path=lambda: os.path.join(current_app.root_path, "static", "images", "headers"),
	#			url_relative_path="images/headers/",
	#			namegen=lambda obj, file_data: secure_filename(file_data.filename),
	#			allowed_extensions=("jpg", "jpeg", "png", "webp"),
	#		)
	#	}


    form_widget_args = {
        "image_url": {
            "placeholder": "/static/images/headers/slide1.webp"
        }
    }

    form_args = {
        "image_url": {"validators": [DataRequired()]},
    }

    def _img_thumb(self, context, model, name):
        if not model.image_url:
            return ""
        return Markup(
            f'<img src="{model.image_url}" '
            f'style="height:40px;width:auto;border-radius:6px;object-fit:cover;">'
        )

    column_formatters = {"image_url": _img_thumb}

    def on_model_change(self, form, model, is_created):
        if model.image_url:
            v = str(model.image_url).strip().replace("\\", "/")

            # If only filename given
            if "/" not in v:
                v = f"images/headers/{v}"

            # Ensure /static prefix
            if not v.startswith("/static/"):
                v = "/static/" + v.lstrip("/")

            model.image_url = v

        super().on_model_change(form, model, is_created)
    
   
class FacultyView(SecureModelView):
    column_list = ("display_order", "name", "designation", "photo_url", "is_published")
    column_sortable_list = ("display_order", "name", "designation", "is_published")
    column_default_sort = ("display_order", True)

    form_columns = (
        "display_order",
        "name",
        "designation",
        "specialization",
        "email",
        "phone",
        "photo_url",
        "bio_html",
        "is_published",
    )
    
    form_widget_args = {
        "photo_url": {"placeholder": "/static/images/faculty/john_doe.webp"}
    }


    # Upload into: app/static/images/faculty/
    # form_extra_fields = {
    #     "photo_url": ImageUploadField(
    #         "Faculty Photo",
    #         base_path=lambda: os.path.join(current_app.root_path, "static", "images", "faculty"),
    #         url_relative_path="images/faculty/",
    #         namegen=lambda obj, file_data: secure_filename(file_data.filename),
    #         allowed_extensions=("jpg", "jpeg", "png", "webp"),
    #     )
    # }

     # ✅ IMPORTANT: formatter signature must be (view, context, model, name)
    def _photo_thumb(view, context, model, name):
        if not getattr(model, "photo_url", None):
            return ""
        return Markup(
            f'<img src="{model.photo_url}" '
            f'style="height:40px;width:40px;border-radius:6px;object-fit:cover;">'
        )

    column_formatters = {"photo_url": _photo_thumb}
    column_formatters_detail = {"photo_url": _photo_thumb}  # optional: detail page too

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

    # Manual path input
    form_columns = ("display_order", "title", "category", "year", "is_published", "cover_image_url")
    form_args = {
        "cover_image_url": {"validators": [DataRequired()]},  # require path if upload image, comment the line
    }

    # ✅ cover upload
  #  form_extra_fields = {
   #     "cover_image_url": ImageUploadField(
    #        "Album Cover",
     #       base_path=lambda: os.path.join(current_app.root_path, "static", "images", "gallery"),
      #      url_relative_path="images/gallery/",
       #     namegen=lambda obj, file_data: secure_filename(file_data.filename),
        #    allowed_extensions=("jpg", "jpeg", "png", "webp"), ) }

    form_widget_args = {
    "cover_image_url": {
        "placeholder": "/static/images/gallery/yourfile.webp"
    }
}

    def _cover_thumb(self, context, model, name):
        if not model.cover_image_url:
            return ""
        return Markup(
            f'<img src="{model.cover_image_url}" '
            f'style="height:40px;width:auto;border-radius:6px;object-fit:cover;">'
        )

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


   
from markupsafe import Markup
from wtforms.validators import DataRequired

class PageView(SecureModelView):
    # ✅ only few columns in list
    column_list = ("title", "slug", "is_published", "show_in_menu")
    column_sortable_list = ("title", "slug", "is_published", "show_in_menu")
    column_searchable_list = ("title", "slug")
    column_default_sort = ("title", True)

    # ✅ do not show big fields in list
    column_exclude_list = ("body_html", "created_at", "updated_at")

    # ✅ keep in form (edit page needs body_html)
    form_columns = (
        "title",
        "slug",
        "header_image_url",
        "header_subtitle",
        "body_html",
        "is_published",
        "show_in_menu",
    )

    form_widget_args = {
        "header_image_url": {"placeholder": "/static/images/headers/page_header.webp"}
    }

    def on_model_change(self, form, model, is_created):
        # normalize header image path
        if getattr(model, "header_image_url", None):
            v = str(model.header_image_url).strip().replace("\\", "/")
            if v:
                if "/" not in v:
                    v = f"images/headers/{v}"
                if not v.startswith("/static/"):
                    v = "/static/" + v.lstrip("/")
            model.header_image_url = v
        super().on_model_change(form, model, is_created)

    
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

""" class NewsView(SecureModelView):
    def on_model_change(self, form, model, is_created):
        if model.cover_image_url:
            v = str(model.cover_image_url).strip().replace("\\", "/")
            if v and not v.startswith("/"):
                v = "/" + v
            model.cover_image_url = v
        super().on_model_change(form, model, is_created) """


from markupsafe import Markup
from wtforms.validators import DataRequired

class NewsView(SecureModelView):
    column_list = ("published_on", "title", "summary", "is_published")
    column_sortable_list = ("published_on", "title", "is_published")
    column_searchable_list = ("title",)
    column_default_sort = ("published_on", True)

    column_exclude_list = ("body_html", "created_at", "updated_at")

    # adjust field names if your model differs
    form_columns = (
        "title",
        "slug",              # if exists; remove if your News model has no slug
        "published_on",      # if exists; else use "date"
        "cover_image_url",
        "summary",           # if exists; else remove
        "body_html",
        "is_published",
    )

    form_widget_args = {
        "cover_image_url": {"placeholder": "/static/images/news/news1.webp"}
    }

    def _cover_thumb(view, context, model, name):
        if not getattr(model, "cover_image_url", None):
            return ""
        return Markup(
            f'<img src="{model.cover_image_url}" '
            f'style="height:40px;width:70px;border-radius:6px;object-fit:cover;">'
        )

    column_formatters = {"cover_image_url": _cover_thumb}

    def on_model_change(self, form, model, is_created):
        if model.cover_image_url:
            v = str(model.cover_image_url).strip().replace("\\", "/")

            # filename only -> images/news/...
            if "/" not in v:
                v = f"images/news/{v}"

            # ensure /static prefix
            if not v.startswith("/static/"):
                v = "/static/" + v.lstrip("/")

            model.cover_image_url = v

        super().on_model_change(form, model, is_created)

        from markupsafe import Markup

class EventView(SecureModelView):
    column_list = ("starts_at", "title", "location", "is_published")
    column_sortable_list = ("starts_at", "title","location", "is_published")
    column_searchable_list = ("title","starts_at","location")
    column_default_sort = ("starts_at", True)

    column_exclude_list = ("description_html", "created_at", "updated_at")

    form_columns = (
        "title",
        "location",              # if exists; remove if not
        "starts_at",        # if your model uses different field name, change it
        "ends_at",          # if exists
        "registration_link",
        "description_html",
        "is_published",
    )
    # the below portion is Not required for Event View
    """ form_widget_args = {
        "cover_image_url": {"placeholder": "/static/images/events/event1.webp"}
    }

    def _cover_thumb(view, context, model, name):
        if not getattr(model, "cover_image_url", None):
            return ""
        return Markup(
            f'<img src="{model.cover_image_url}" '
            f'style="height:40px;width:70px;border-radius:6px;object-fit:cover;">'
        )

    column_formatters = {"cover_image_url": _cover_thumb}

    def on_model_change(self, form, model, is_created):
        if model.cover_image_url:
            v = str(model.cover_image_url).strip().replace("\\", "/")
            if "/" not in v:
                v = f"images/events/{v}"
            if not v.startswith("/static/"):
                v = "/static/" + v.lstrip("/")
            model.cover_image_url = v
        super().on_model_change(form, model, is_created) """