from cms.models import *
from cms.models.main import Page, Section
from home.settings import VERSION

__author__ = ''


def populate_db():
    pages = Page.objects.all()
    if pages.count() == 0:
        create_home_site()
    else:
        print('Database already populated')


def create_home_site():
    page = Page(page_name='home', position=0, is_enabled=True)
    page.save()
    section = Section(page=page, content="Thanks for installing "
                                         "Cypetulip " + VERSION)
    section2 = Section(page=page, content="Configure this site !")
    section.save()
    section2.save()


def register_site(page_name, link):
    page = Page(page_name=page_name, position=1, is_enabled=True,
                link=link)
    page.save()



