

![image](https://cloud.bwk-technik.de/thumbnail/af528f4e3ecf400195c7/1024/cp_s.png)

CypeTulip is a free open source e-commerce system. Its strength is its highly flexible product systeem,
that allows both digital and regular products, but also customizable products.
Products can require file uploads, selects, or number-/checkbox inputs.  

## Current Features
- E-commerce 
    - Shopping cart
    - Free configurable products (as described above)
    - On request products
    - Categories
    - System Vouchers (fixed price and percentage)
    - Dynamic Product attributes / including filtering
- CMS
    - Pages
    - Sections (WYSIWYG)
    - Header / Footer
- Payment methods:
    - Prepayment
    - Bill
    - Paypal 
- Management
    - Basic management functionality (Add/edit products, subproducts, categories, ...)
    - Manually create orders / clients
    - Accounting Dashboard
    - Create order from on request product
- Other
    - LDAP Support
    - SMTP Support
    
## Planned Features
- Other payment providers
- RMA
- Web hooks for (almost) all transactions
- Communication Log
- CSV Export
- Reviews
- Wishlist
- Shipper Integration (DHL,...)


# Development

System requirements:
- Python >3.7
- Django >3.1.0


#Installation

Run the setup
```
python manage.py setup
```
