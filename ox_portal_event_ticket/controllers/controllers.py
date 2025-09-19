# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from operator import itemgetter
from odoo.tools.translate import _
from odoo import _, fields
from odoo.osv.expression import OR, AND
from dateutil.relativedelta import relativedelta
from odoo.tools import groupby as groupbyelem
from datetime import datetime, date, timedelta
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.portal import CustomerPortal

class EventPortal(CustomerPortal):

    def get_domain_my_event(self, user):
        return [
            ('partner_id.id', '=', user.partner_id.id)
        ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user  = request.env.user
        if 'event_count' in counters:
            values['event_count'] = request.env['event.registration'].search_count(self.get_domain_my_event(request.env.user))
        return values

    def _event_get_page_view_values(self, event, access_token, **kwargs):
        values = {
            'page_name': 'events',
            'event': event,
        }
        return self._get_page_view_values(event, access_token, values, 'my_event_history', False, **kwargs)

    def _get_searchbar_inputs(self):
        return {
            'all': {'input': 'all', 'label': _('Search in All')},
            'name': {'input': 'name', 'label': _('Search by Attendee')},
            'event': {'input': 'event', 'label': _('Search by Event')},
        }

    @http.route(['/my/events', '/my/events/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_events(self, page=1, date_begin=None, date_end=None, search=None, search_in='all', sortby=None, filterby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        EventRegistration = request.env['event.registration']
        domain = self.get_domain_my_event(request.env.user)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': []},
            'this week': {'label': _('This Week'), 'domain': []},
            'last week': {'label': _('Last Week'), 'domain': []},
            'this month': {'label': _('This Month'), 'domain': []},
            'last month': {'label': _('Last Month'), 'domain': []},
            'this year': {'label': _('This Year'), 'domain': []},
            'last year': {'label': _('Last Year'), 'domain': []},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'event': {'input': 'event_id', 'label': _('Event')},
        }

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'}
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        format_str = '%d%m%Y'

        if not filterby:
            filterby = 'all'

        if filterby == 'today':
            my_datetime_field = datetime.now()
            start_of_day = my_datetime_field.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = my_datetime_field.replace(hour=23, minute=59, second=59, microsecond=999999)
            start_of_day_str = start_of_day.strftime('%Y-%m-%d %H:%M:%S')
            end_of_day_str = end_of_day.strftime('%Y-%m-%d %H:%M:%S')
            start = fields.Datetime.to_datetime(start_of_day_str)
            end = fields.Datetime.to_datetime(end_of_day_str)
            domain += [('create_date','>=',start), ('create_date','<=', end)]

        if filterby == 'this week':
            domain+=[('create_date','<=', ((date.today() - relativedelta(days=1, weeks=-1)).strftime('%Y-%m-%d'))),
            ('create_date','>=', ((date.today() - relativedelta(days=7, weeks=-1)).strftime('%Y-%m-%d')))]

        if filterby == 'last week':
            domain+=[('create_date','>=', ((date.today()  + relativedelta(days=0, weeks=-1)).strftime('%Y-%m-%d'))),
            ('create_date','<=', ((date.today()  + relativedelta(days=6, weeks=-1)).strftime('%Y-%m-%d')))]

        if filterby == 'this month':
            from_month = []
            to_month = []
            from_month.append('01')
            month = '{:02d}'.format(date.today().month)
            from_month.append(str(month))
            from_month.append(str(date.today().year))
            to_month.append('30')
            to_month.append(str(month))
            to_month.append(str(date.today().year))
            from_string = ''.join(from_month)
            to_string = ''.join(to_month)
            from_date = datetime.strptime(from_string, format_str)
            to_date = datetime.strptime(to_string, format_str)
            domain+=[('create_date','>=',from_date),('create_date','<=',to_date)]

        if filterby == 'last month':
            from_month = []
            to_month = []
            from_month.append('01')
            month = '{:02d}'.format(date.today().month-1)
            from_month.append(str(month))
            from_month.append(str(date.today().year))
            if month == '02':
                to_month.append('28')
            else:
                to_month.append('30')
            to_month.append(str(month))
            to_month.append(str(date.today().year))
            from_string = ''.join(from_month)
            to_string = ''.join(to_month)
            from_date = datetime.strptime(from_string, format_str)
            to_date = datetime.strptime(to_string, format_str)
            domain+=[('create_date','>=',from_date),('create_date','<=',to_date)]

        if filterby == 'this year':
            from_month = []
            to_month = []
            from_month.append('01')
            from_month.append('01')
            from_month.append(str(date.today().year))
            to_month.append('30')
            to_month.append('12')
            to_month.append(str(date.today().year))
            from_string = ''.join(from_month)
            to_string = ''.join(to_month)
            from_date = datetime.strptime(from_string, format_str)
            to_date = datetime.strptime(to_string, format_str)
            domain+=[('create_date','>=',from_date),('create_date','<=',to_date)]

        if filterby == 'last year':
            from_month = []
            to_month = []
            from_month.append('01')
            from_month.append('01')
            from_month.append(str(date.today().year-1))
            to_month.append('30')
            to_month.append('12')
            to_month.append(str(date.today().year-1))
            from_string = ''.join(from_month)
            to_string = ''.join(to_month)
            from_date = datetime.strptime(from_string, format_str)
            to_date = datetime.strptime(to_string, format_str)
            domain+=[('create_date','>=',from_date),('create_date','<=',to_date)]

        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        if search and search_in:
            search_domain = []

            if search_in in ('all'):
                search_domain = ['|','|', ('event_id.name', 'ilike', search), ('name', 'ilike', search), ('email', 'ilike', search)]

            if search_in in ('name'):
                search_domain = [('name', 'ilike', search)]

            if search_in in ('event'):
                search_domain = [('event_id.name', 'ilike', search)]

            domain += search_domain

        # pager
        event_count = EventRegistration.search_count(domain)
        pager = portal_pager(
            url='/my/events',
            url_args={'date_begin': date_begin, 'date_end': date_end,'sortby': sortby, 'search_in': search_in, 'search': search},
            total=event_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        events = EventRegistration.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        if groupby == 'event':
            grouped_events = [request.env['event.registration'].concat(*g) for k, g in groupbyelem(events, itemgetter('event_id'))]
        else:
            grouped_events = [events]

        searchbar_inputs = self._get_searchbar_inputs()

        values.update({
            'date': date_begin,
            'grouped_events': grouped_events,
            'page_name': 'events',
            'default_url': '/my/events',
            'pager': pager,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("ox_portal_event_ticket.portal_my_events", values)
    
    @http.route([
        "/event/<int:event_id>",
        "/event/<int:event_id>/<access_token>",
        '/my/event/<int:event_id>',
        '/my/event/<int:event_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def event_followup(self, event_id=None, report_type=None, download=False, access_token=None, **kw):
        try:
            event_sudo = self._document_check_access('event.registration', event_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        request.session['event_id'] = True
        values = self._event_get_page_view_values(event_sudo, access_token, **kw)
        return request.render("ox_portal_event_ticket.event_followup", values)

    @http.route('/event/ticket/report/<int:event_id>', type='http', auth='user')
    def download_qweb_report(self, event_id=None, access_token=None, **kw):
        try:
            event_sudo = self._document_check_access('event.registration', event_id, access_token)
        except (AccessError, MissingError): 
            return request.redirect('/my')
        pdf = request.env["ir.actions.report"].sudo()._render_qweb_pdf('event.action_report_event_registration_full_page_ticket', event_sudo.id)[0]
        report_name = event_sudo.name +'.pdf'
        return request.make_response(pdf, headers=[('Content-Type', 'application/pdf'),('Content-Disposition', content_disposition(report_name))])