from odoo.addons.restful.common import (
    make_json_response,
    _has_data
)
from odoo import http
from odoo.http import request
from odoo.addons.restful.controllers.main import validate_token
from datetime import date,datetime


class EventController(http.Controller):
    @validate_token
    @http.route('/api/calendar/events',auth='none', method=['GET'])
    def index(self):
        events = self._all()
        rows = []
        response = {
            'count': len(rows),
            'rows': rows
        }
        today_date = date.today()
        today_datetime = datetime.now()
        for event in events:
            print(event)
            if event.allday:
                if event.stop_date >= today_date:
                    rows.append(self._to_json(event))
            else:
                if event.stop_datetime >= today_datetime:
                    rows.append(self._to_json(event))

        return make_json_response(response)

    def _all(self, limit=None):
        if limit is not None:
            return request.env['calendar.event'].sudo().search([], limit=limit)
        return request.env['calendar.event'].sudo().search([])

    def _to_json(self, event):
        if event.allday:
            response = {
                "id": event.id,
                "title": event.name,
                "description": _has_data(event.description),
                "location": _has_data(event.location),
                "all_day": event.allday,
                "start_date": event.start_date.isoformat(),
                "end_date": event.stop_date.isoformat()
            }
        else:
            response = {
                "id": event.id,
                "title": event.name,
                "description": _has_data(event.description),
                "location": _has_data(event.location),
                "all_day": event.allday,
                "start_datetime": event.start_datetime.isoformat(),
                "stop_datetime": event.stop_datetime.isoformat(),
                "duration": event.duration
            }

        if event.alarm_ids:
            rows = []
            for alarm in event.alarm_ids:
                rows.append({
                    "name": alarm.name,
                    "unit_name": alarm.interval,
                    "duration": alarm.duration,
                    "duration_minutes": alarm.duration_minutes
                })
            response['reminders'] = rows
        else:
            response['reminders'] = []

        if event.recurrency:
            response['recurrent'] = {
                "interval": event.interval,
                "range_unit": event.rrule_type
            }
            response['attendees'] = self._get_attendees(int(event.id[:1]))
        else:
            response['recurrent'] = ''
            response['attendees'] = self._get_attendees(event.id)

        return response

    def _get_attendees(self, event_id):
        attendees = request.env['calendar.attendee'].search([['event_id','=',event_id]])
        rows = []
        for attendee in attendees:
            rows.append({
                "attendee_id": attendee.partner_id.id,
                "name": attendee.partner_id.name
                }
            )
        return rows