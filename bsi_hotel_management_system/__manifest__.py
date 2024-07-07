# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Hotel Management System',
    'version' : '15',
    'summary': 'Hotel Management System',
    'sequence': -100,
    'description': """
Hotel Management System
====================
    """,
    'category': 'Management',
    'website': 'https://www.google.com',
    'depends' : ['sale','account','base','hr','base_setup', 'product', 'analytic', 'portal', 'digest','website','website_payment', 'board','auth_signup'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'report/room_invoice_detail_template.xml',
        'report/booking_detail_order_template.xml',
        'report/report.xml',

        'data/mail_invoice_template_data.xml',
        'data/send_booking_status_template.xml',
        'data/forgot_password_mail_template.xml',
        
        'data/sequence.xml',
        'data/cron.xml',

        
        'wizard/register_payment.xml',

        'views/Room.xml',
        'views/Facility.xml',
        'views/Service.xml',
        'views/Booking_Detail.xml',
        'views/room_invoices.xml',
        'views/Dashboard.xml',
        'views/menus.xml',

        
        'static/xml/index.xml',
        'static/xml/user_profile.xml',
        'static/xml/change_password_page.xml',
        'static/xml/create_new_password.xml',
        'static/xml/check_email.xml',
        'static/xml/forgot_password.xml',
        'static/xml/rooms.xml',
        'static/xml/individual_room.xml',
        'static/xml/booking.xml',
        'static/xml/register_template.xml',
        'static/xml/login_template.xml',
        'static/xml/booking.xml',
        'static/xml/contact.xml',
        'static/xml/about.xml',
        'static/xml/my_bookings.xml',
        'static/xml/booking_detail_page.xml',
        'static/xml/header_footer.xml',
    ],
    'demo': [
    ],
    'assets':{
        'web.assets_frontend':[
            'bsi_hotel_management_system/static/src/css/main.css',
            'bsi_hotel_management_system/static/src/css/font-awesome.min.css',
            'bsi_hotel_management_system/static/src/css/bootstrap.min.css',
            'bsi_hotel_management_system/static/src/css/elegant-icons.css',
            'bsi_hotel_management_system/static/src/css/flaticon.css',
            'bsi_hotel_management_system/static/src/css/jquery-ui.min.css',
            'bsi_hotel_management_system/static/src/css/magnific-popup.css',
            'bsi_hotel_management_system/static/src/css/nice-select.css',
            'bsi_hotel_management_system/static/src/css/slicknav.min.css',
            'bsi_hotel_management_system/static/src/css/owl.carousel.min.css',
            'bsi_hotel_management_system/static/src/css/style.css',
            # 'bsi_hotel_management_system/static/src/js/bootstrap.min.js',
            # 'bsi_hotel_management_system/static/src/js/jquery-3.3.1.min.js',
            'bsi_hotel_management_system/static/src/js/jquery-ui.min.js',
            'bsi_hotel_management_system/static/src/js/jquery.magnific-popup.min.js',
            'bsi_hotel_management_system/static/src/js/jquery.nice-select.min.js',
            'bsi_hotel_management_system/static/src/js/jquery.slicknav.js',
            'bsi_hotel_management_system/static/src/js/owl.carousel.min.js',
            'bsi_hotel_management_system/static/src/js/main.js',
            'bsi_hotel_management_system/static/src/js/search_funcationality.js',
            'bsi_hotel_management_system/static/src/js/form_submit.js',

        ],
        'web.assets_common':[
            'bsi_hotel_management_system/static/src/js/popup.js',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'license': 'LGPL-3',
}