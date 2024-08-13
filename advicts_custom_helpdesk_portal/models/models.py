# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HelpDeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    allow_portal_ticket_reopen = fields.Boolean('Customer Reopen')
    reopen_stage = fields.Many2one(
        'helpdesk.stage',
        domain="[('id', 'in', stage_ids)]",  # Domain to filter stages by current team's stages
        string='Reopen Stage'
    )


class HelpDeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    reopen_reason = fields.Text('Reopen Reason', tracking=True)
    portal_attachment_ids = fields.Many2many('ir.attachment', string='Portal Attachments')