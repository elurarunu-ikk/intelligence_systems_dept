from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from sqlalchemy import desc
from ...extensions import db
from flask import url_for
from ...models import (
    SiteSettings, Page, Program, Faculty, News, Event, Achievement,
    FundedProject, MoU, PlacementStat, Newsletter, Enquiry,
    GalleryAlbum, GalleryImage,Alumni,HeroSlide
)

public_bp = Blueprint("public", __name__)

def get_settings():
    s = SiteSettings.query.first()
    if not s:
        s = SiteSettings()
        db.session.add(s)
        db.session.commit()
    return s

@public_bp.get("/")
def home():
    settings = get_settings()  

    slides = (HeroSlide.query
              .filter_by(is_active=True)
              .order_by(HeroSlide.order.asc(), HeroSlide.created_at.desc())
              .all())

    about_page = Page.query.filter_by(slug="about", is_published=True).first()

    programs_ug = Program.query.filter_by(level="UG", is_published=True).all()
    programs_pg = Program.query.filter_by(level="PG", is_published=True).all()
    programs_res = Program.query.filter_by(level="Research", is_published=True).all()

    news = News.query.filter_by(is_published=True).order_by(desc(News.published_on)).limit(4).all()
    events = Event.query.filter_by(is_published=True).order_by(Event.starts_at.desc()).limit(4).all()
    achievements = Achievement.query.filter_by(is_published=True).order_by(desc(Achievement.is_featured), desc(Achievement.created_at)).limit(6).all()
    mous = MoU.query.filter_by(is_published=True).limit(8).all()
    placement_stats = PlacementStat.query.filter_by(is_visible=True).limit(6).all()
   # alumni = Alumni.query.order_by(Alumni.is_featured.desc(), Alumni.created_at.desc()).limit(6).all()

    return render_template("public/home.html",
                           settings=settings,
                           slides=slides,
                           about_page = about_page, 
                           programs_ug=programs_ug,
                           programs_pg=programs_pg,
                           programs_res=programs_res,
                           news=news,
                           events=events,
                           achievements=achievements,
                           mous=mous,
                           placement_stats=placement_stats,
                           #alumni=alumni)
                         )

@public_bp.get("/p/<slug>")
def page_by_slug(slug):
    settings = get_settings()
    page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()

    # normalize banner URL
    if page.header_image_url:
        if page.header_image_url.startswith("/static/") or page.header_image_url.startswith("http"):
            header_image = page.header_image_url
        else:
            header_image = url_for("static", filename=page.header_image_url)
    else:
        header_image = url_for("static", filename="images/headers/default.jpg")

    return render_template(
        "public/page.html",
        settings=settings,
        page=page,
        header_image=header_image,
        header_title=page.title,
        header_subtitle=page.header_subtitle
    )


@public_bp.get("/about")
def about():
    settings = get_settings()
    page = Page.query.filter_by(slug="about", is_published=True).first()

    # ✅ normalize banner URL
    if page and page.header_image_url:
        if page.header_image_url.startswith("/static/") or page.header_image_url.startswith("http"):
            header_image = page.header_image_url
        else:
            header_image = url_for("static", filename=page.header_image_url)
    else:
        header_image = url_for("static", filename="images/headers/about.jpg")

    return render_template(
        "public/page.html",
        settings=settings,
        page=page,
        fallback_title="About",
        header_image=header_image,
        header_title="About",
        header_subtitle=(page.header_subtitle if page and page.header_subtitle else "Aim, scope, vision, and facilities"),
    )
@public_bp.get("/academics")
def academics():
    settings = get_settings()
    programs = Program.query.filter_by(is_published=True).all()
    return render_template("public/academics.html", settings=settings, programs=programs)

@public_bp.get("/faculty")
def faculty():
    settings = get_settings()
    faculty_list = (Faculty.query
              .filter_by(is_published=True)
              .order_by(Faculty.display_order.asc())
              .all()
                )
    return render_template("public/faculty.html", 
                           settings=settings, 
                           faculty_list=faculty_list,
                           header_image=settings.banner_faculty,
                           header_title="Faculty",
                           header_subtitle="Meet our academic team"
                           )

@public_bp.get("/research")
def research():
    settings = get_settings()
    projects = FundedProject.query.filter_by(is_published=True).order_by(FundedProject.created_at.desc()).all()
    return render_template("public/research.html", settings=settings, projects=projects)

@public_bp.get("/placements")
def placements():
    settings = get_settings()
    stats = PlacementStat.query.filter_by(is_visible=True).all()
    mous = MoU.query.filter_by(is_published=True).all()
    return render_template("public/placements.html", settings=settings, stats=stats, mous=mous)

@public_bp.get("/news")
def news_list():
    settings = get_settings()
    items = News.query.filter_by(is_published=True).order_by(desc(News.published_on)).all()
    return render_template("public/news_list.html", 
                           settings=settings, 
                           items=items,
                           header_image=settings.banner_news,
                           header_title="News & Updates",
                           header_subtitle="Latest announcements and achievements"
                           )

@public_bp.get("/news/<slug>")
def news_detail(slug: str):
    settings = get_settings()
    item = News.query.filter_by(slug=slug, is_published=True).first()
    if not item:
        abort(404)
    return render_template("public/news_detail.html", settings=settings, item=item,)

@public_bp.get("/events")
def events_list():
    settings = get_settings()
    items = Event.query.filter_by(is_published=True).order_by(Event.starts_at.desc()).all()
    return render_template("public/events_list.html", 
                           settings=settings, 
                           items=items,
                            header_image=settings.banner_events,
                            header_title="Events",
                            header_subtitle="Academic and campus events"
                           )

@public_bp.get("/newsletter")
def newsletter():
    settings = get_settings()
    items = Newsletter.query.filter_by(is_published=True).order_by(Newsletter.published_on.desc()).all()
    return render_template("public/newsletter.html", settings=settings, items=items)

@public_bp.get("/contact")
def contact():
    settings = get_settings()
    return render_template("public/contact.html", settings=settings)

@public_bp.post("/contact")
def contact_post():
    name = request.form.get("name","").strip()
    email = request.form.get("email","").strip()
    phone = request.form.get("phone","").strip()
    message = request.form.get("message","").strip()

    if not name or not email or not message:
        flash("Please fill name, email and message.", "danger")
        return redirect(url_for("public.contact"))

    db.session.add(Enquiry(name=name, email=email, phone=phone, message=message))
    db.session.commit()
    flash("Thank you! Your enquiry has been submitted.", "success")
    return redirect(url_for("public.contact"))

@public_bp.get("/gallery")
def gallery():
    settings = get_settings()
    albums = GalleryAlbum.query.filter_by(is_published=True).order_by(GalleryAlbum.year.desc()).all()
    return render_template(
        "public/gallery.html",
        settings=settings,
        albums=albums,
        header_title="Gallery",
        header_subtitle="Events, Workshops, Alumni Meets"
    )
@public_bp.get("/gallery/<int:album_id>")
def gallery_album(album_id):
    settings = get_settings()
    album = GalleryAlbum.query.filter_by(id=album_id, is_published=True).first_or_404()
    return render_template("public/gallery_album.html", settings=settings, album=album)

@public_bp.get("/alumni")
def alumni():
    settings = get_settings()
    alumni_list = Alumni.query.order_by(Alumni.graduation_year.desc()).all()
    return render_template(
        "public/alumni.html",
        settings=settings,
        alumni=alumni_list,
        header_title="Alumni",
        header_subtitle="Our Graduates, Our Pride"
    )



