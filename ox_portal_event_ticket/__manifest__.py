# -*- coding: utf-8 -*-
{
    'name': "Portal Event Ticket | Event Ticket View in Portal Odoo App",
    'version': '18.0.0.0',
    'category': 'Website',
    'summary': "Online event portal view website event ticket portal event registration portal view website event portal event booking portal event website portal for event management portal print ticket print event ticket print pass print event pass download ticket",
    'description': """Portal Event Ticket Odoo app is versatile that allows users to access event tickets directly through their online portal. One of the key features of this app is the ability to view and download event tickets direct from the portal. Users can also sort event tickets by different type of options like newest arrivals, and ticket names.""",
    'author': "OutsetX",
    "website" : 'https://www.outsetx.com',
    'depends': ['base','website','portal','event','website_event'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    "qweb" : [],
    "auto_install": False,
    "installable": True,
    "license":'OPL-1',
}
