from __future__ import annotations
from datetime import datetime
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(UserMixin, db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class SiteSettings(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(255), default="Department of Intelligence Systems", nullable=False)
    university_name = db.Column(db.String(255), default="SIMATS Deemed University (Saveetha Institute of Medical and Technical Sciences)", nullable=False)
    tagline = db.Column(db.String(255), default="Shaping Intelligent Systems for a Smarter Future", nullable=False)
    hero_title = db.Column(db.String(255), default="Department of Intelligence Systems", nullable=False)
    hero_subtitle = db.Column(db.String(500), default="Outcome-focused education, strong mentorship, and research-led learning.", nullable=False)
    enquiry_email = db.Column(db.String(255), default="intelligencesystems@saveetha.edu.in", nullable=False)
    phone = db.Column(db.String(50), default="+91-XXXXXXXXXX", nullable=False)
    address = db.Column(db.Text, default="Saveetha University, Chennai, Tamil Nadu, India", nullable=False)
    google_map_embed = db.Column(db.Text, default="", nullable=True)

     # Section banner images
    banner_faculty = db.Column(db.String(500), nullable=True)
    banner_news = db.Column(db.String(500), nullable=True)
    banner_events = db.Column(db.String(500), nullable=True)

class Page(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    body_html = db.Column(db.Text, nullable=False, default="")
    
    header_image_url = db.Column(db.String(500), nullable=True)
    header_subtitle = db.Column(db.String(255), nullable=True)

    is_published = db.Column(db.Boolean, default=True, nullable=False)
    show_in_menu = db.Column(db.Boolean, default=False, nullable=False)

class Program(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)  # UG/PG/Research
    name = db.Column(db.String(255), nullable=False)
    overview_html = db.Column(db.Text, default="", nullable=False)
    eligibility = db.Column(db.String(255), default="Editable", nullable=False)
    duration = db.Column(db.String(100), default="Editable", nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

class Faculty(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    designation = db.Column(db.String(255), default="Faculty", nullable=False)
   
    # NEW – simple ordering
    display_order = db.Column(db.Integer, default=100, nullable=False)

    specialization = db.Column(db.String(255), default="Editable", nullable=False)
    email = db.Column(db.String(255), default="editable@saveetha.edu.in", nullable=False)
    phone = db.Column(db.String(50), default="", nullable=True)
    photo_url = db.Column(db.String(500), default="", nullable=True)
    bio_html = db.Column(db.Text, default="", nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

class News(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(500), default="", nullable=False)
    body_html = db.Column(db.Text, default="", nullable=False)
    cover_image_url = db.Column(db.String(500), default="", nullable=True)
    published_on = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

class Event(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), default="Saveetha University, Chennai", nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ends_at = db.Column(db.DateTime, nullable=True)
    registration_link = db.Column(db.String(500), default="", nullable=True)
    description_html = db.Column(db.Text, default="", nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

class Achievement(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(120), default="Student", nullable=False)
    year = db.Column(db.String(10), default="2025", nullable=False)
    description = db.Column(db.String(800), default="", nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

class FundedProject(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    sponsor = db.Column(db.String(255), default="Editable", nullable=False)
    amount = db.Column(db.String(120), default="Editable", nullable=False)
    duration = db.Column(db.String(120), default="Editable", nullable=False)
    pi = db.Column(db.String(255), default="Editable", nullable=False)
    summary = db.Column(db.String(800), default="", nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

class MoU(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    partner_name = db.Column(db.String(255), nullable=False)
    area = db.Column(db.String(255), default="Industry Collaboration", nullable=False)
    signed_on = db.Column(db.Date, nullable=True)
    logo_url = db.Column(db.String(500), default="", nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

class PlacementStat(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(120), nullable=False)   # e.g., Highest Package
    value = db.Column(db.String(120), nullable=False)   # e.g., 18 LPA
    is_visible = db.Column(db.Boolean, default=True, nullable=False)

class Newsletter(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    issue = db.Column(db.String(50), default="Vol 1, Issue 1", nullable=False)
    published_on = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    pdf_url = db.Column(db.String(500), default="", nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

class Enquiry(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), default="", nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="New", nullable=False)  # New / In Progress / Closed

class GalleryAlbum(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    #slug = db.Column(db.String(200), unique=True, nullable=False)   # ADD THIS
    category = db.Column(db.String(100), default="Event", nullable=False)
    year = db.Column(db.String(10), default="2025", nullable=False)
    cover_image_url = db.Column(db.String(500), default="", nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

    def __str__(self):
        return self.title

class GalleryImage(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey("gallery_album.id"), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(255), default="", nullable=True)

    album = db.relationship("GalleryAlbum", backref=db.backref("images", lazy=True,order_by="GalleryImage.id.asc()"))

class Alumni(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    graduation_year = db.Column(db.String(10), nullable=False)
    current_position = db.Column(db.String(255), default="", nullable=True)
    organization = db.Column(db.String(255), default="", nullable=True)
    photo_url = db.Column(db.String(500), default="", nullable=True)
    profile_html = db.Column(db.Text, default="", nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

class HeroSlide(db.Model, TimestampMixin):
    __tablename__ = "hero_slides"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=True)
    subtitle = db.Column(db.String(500), nullable=True)

    image_url = db.Column(db.String(500), nullable=False)   # URL or /static/... or /uploads/...
    cta_text = db.Column(db.String(80), nullable=True)
    cta_url = db.Column(db.String(500), nullable=True)

    order = db.Column(db.Integer, default=1, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)



