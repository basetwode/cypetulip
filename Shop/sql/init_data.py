from CMS.sql.init_data import register_site

__author__ = ''


def populate_db():
    # pages = Page.objects.all()
    # if pages.count() > 0:
    #     create_home_site()
    #
    # else:
    #     print 'Database already populated'
    register_site('Products', '/shop/products/')
    print('Product site registered')
