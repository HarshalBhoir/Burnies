{
    'name': 'Auto Generate Product Barcode (EAN13)',
    'version': '1.0.2',
    'category': 'Tools',
    'author': 'FreelancerApps',
    'summary': 'Auto Generate Company Wise Product EAN13 barcode, In Different Size, different color, Barcode Create Using Random Number/Current Date/Any Prefix auto generate product barcode ean13 auto generate product barcode auto generate product ean13 auto generate barcode product auto generate barcode ean13 auto product generate barcode auto generate ean13 product auto generate ean13 barcode auto product generate ean13 auto product barcode generate auto product barcode ean13 auto barcode generate product auto barcode generate ean13 auto barcode product generate auto product ean13 barcode auto product ean13 generate auto barcode product ean13 generate auto product barcode auto ean13 generate product auto barcode ean13 generate auto barcode ean13 product auto ean13 generate barcode auto ean13 product generate auto ean13 product barcode generate auto ean13 generate auto ean13 barcode generate auto ean13 barcode product generate auto barcode ean13 generate product auto ean13 product generate barcode generate product auto ean13 generate product barcode auto ean13 barcode generate product ean13 auto product generate ean13 barcode generate ean13 auto product generate product generate barcode ean13 auto barcode ean13 generate barcode product auto ean13 generate ean13 auto barcode generate ean13 product auto ean13 product barcode ean13 barcode product auto barcode ean13 barcode auto ean13 barcode product ean13 barcode auto generate barcode product ean13 product barcode generate barcode product auto product generate barcode ean13 generate barcode auto barcode product ean13 product auto generate auto barcode product barcode generate barcode auto generate product barcode generate barcode ean13 barcode auto product barcode generate ean13 generate auto product generate auto barcode auto barcode auto ean13 barcode ean13 generate ean13 product generate ean13 generate product ean13 barcode product ean13 auto generate ean13 generate barcode ean13 product ean13 barcode auto ean13 generate ean13 barcode generate auto product auto product ean13 generate product barcode ean13 barcode ean13 auto generate auto barcode ean13 auto ean13 product auto product ean13 auto barcode ean13 product barcode  ean13 auto product ean13 auto generate product generate barcode product auto Restrict Read Only User Hide Any Menu Restrict User Menus multi level approve three level approve Tripple Approve Purchase Tripple Approval Project Checklist Task Checklist website document attachment product attachment',
    'description': """
Auto Generate Product EAN 13 Barcode
====================================
This application is generating product EAN13 barcode automatically (on product creation) or manually.

EAN13 barcode can be created by using a random number or using current date, you can add some prefix to the barcode, you have an
option to auto-generate barcode on product creation, the barcode can be created in different sizes and colors. All setting saved per
company, so different barcode can be created for the different company.

You can create barcode in bulk for already created products, you have the option to select multiple products and create barcode or
select multiple product categories and create the barcode for all product of the selected product category.

Key features:
-------------
* Auto generate EAN13 barcode using random number.
* Auto generate EAN13 barcode using current date.
* Auto generate EAN13 barcode in using some prefix.
* Auto generate EAN13 barcode in different size.
* Auto generate EAN13 barcode in different colors.
* Manage EAN13 barcode font size, Space before and after, text below barcode, distance between them
* Auto generate EAN13 bulk barcode by selecting multiple products.
* Auto generate EAN13 bulk barcode by selecting multiple products categories.
* Company wise barcode generation setting.
* Product can be search by ean13 barcode.

<Search Keyword for internal user only>
---------------------------------------
auto generate product barcode ean13 auto generate product barcode auto generate product ean13 auto generate barcode product auto generate barcode ean13 auto product generate barcode auto generate ean13 product auto generate ean13 barcode auto product generate ean13 auto product barcode generate auto product barcode ean13 auto barcode generate product auto barcode generate ean13 auto barcode product generate auto product ean13 barcode auto product ean13 generate auto barcode product ean13 generate auto product barcode auto ean13 generate product auto barcode ean13 generate auto barcode ean13 product auto ean13 generate barcode auto ean13 product generate auto ean13 product barcode generate auto ean13 generate auto ean13 barcode generate auto ean13 barcode product generate auto barcode ean13 generate product auto ean13 product generate barcode generate product auto ean13 generate product barcode auto ean13 barcode generate product ean13 auto product generate ean13 barcode generate ean13 auto product generate product generate barcode ean13 auto barcode ean13 generate barcode product auto ean13 generate ean13 auto barcode generate ean13 product auto ean13 product barcode ean13 barcode product auto barcode ean13 barcode auto ean13 barcode product ean13 barcode auto generate barcode product ean13 product barcode generate barcode product auto product generate barcode ean13 generate barcode auto barcode product ean13 product auto generate auto barcode product barcode generate barcode auto generate product barcode generate barcode ean13 barcode auto product barcode generate ean13 generate auto product generate auto barcode auto barcode auto ean13 barcode ean13 generate ean13 product generate ean13 generate product ean13 barcode product ean13 auto generate ean13 generate barcode ean13 product ean13 barcode auto ean13 generate ean13 barcode generate auto product auto product ean13 generate product barcode ean13 barcode ean13 auto generate auto barcode ean13 auto ean13 product auto product ean13 auto barcode ean13 product barcode 

ean13 auto product ean13 auto generate product generate barcode product auto Restrict Read Only User Hide Any Menu Restrict User Menus multi level approve three level approve Tripple Approve Purchase Tripple Approval Project Checklist Task Checklist
website document attachment product attachment

""",
    'depends': ['base', 'product'],
    'data': [
        'security/barcode_generation_security.xml',
        'views/company_view.xml',
        'views/product_view.xml',
        'wizard/generate_product_barcode_view.xml',
        'wizard/generate_product_category_barcode_view.xml',
    ],
    'images': ['static/description/auto_generate_ean13_banner.png'],
    'live_test_url': 'https://youtu.be/E9MQj5SQi70',
    'price': 11.99,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
