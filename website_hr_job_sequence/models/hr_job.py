# -*- coding: utf-8 -*-
from unittest import result
from odoo import models, fields, api


class hr_job(models.Model):
    _inherit = 'hr.job'
    _description = "Job Position Sequence"

    sequence_number = fields.Integer(string='Sequence Number', readonly=True, required=True, copy=False, default=0)
    location = fields.Char(string='Location')

    #Overide create function to change the sequence number
    @api.model
    def create(self, vals):
        if vals.get('sequence_number', 0) == 0:
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('hr.job.sequence') or 0
        result = super(hr_job, self).create(vals)
        return result
