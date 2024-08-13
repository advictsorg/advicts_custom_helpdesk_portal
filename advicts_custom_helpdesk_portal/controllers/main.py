from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.translate import _
import base64
import json


class HelpdeskRenew(http.Controller):
    @http.route([
        '/my/ticket/renew/<int:ticket_id>',
        '/my/ticket/renew/<int:ticket_id>/<access_token>'

    ], type='http', auth="public", website=True, methods=['POST'], csrf=False)
    def ticket_renew(self, ticket_id=None, access_token=None, **kw):
        reason = kw.get('reason', '')
        try:
            ticket_sudo = self._check_access('helpdesk.ticket', ticket_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if not ticket_sudo.team_id.allow_portal_ticket_reopen:
            raise UserError(_("The team does not allow ticket Reopen through portal"))

        if not ticket_sudo.closed_by_partner:
            reopen_stage = ticket_sudo.team_id.reopen_stage
            if ticket_sudo.stage_id != reopen_stage:
                ticket_sudo.write({'stage_id': reopen_stage.id})
                body = _('Ticket Reopen by the customer')
                message = _(reason)
                ticket_sudo.with_context(mail_create_nosubscribe=True).message_post(body=body, message_type='comment',
                                                                                    subtype_xmlid='mail.mt_note')
                ticket_sudo.with_context(mail_create_nosubscribe=True).message_post(body=message,
                                                                                    message_type='comment',
                                                                                    subtype_xmlid='mail.mt_comment')
        return request.redirect('/my/ticket/%s/%s' % (ticket_id, access_token or ''))

    def _check_access(self, model_name, record_id, access_token=None):
        record = request.env[model_name].sudo().browse(record_id)
        if access_token:
            record = record.sudo().search([('id', '=', record_id), ('access_token', '=', access_token)], limit=1)
        if not record:
            raise MissingError(_("This record does not exist or has been removed."))
        try:
            record.check_access_rights('read')
            record.check_access_rule('read')
        except AccessError:
            raise AccessError(_("You do not have the necessary access rights."))
        return record
