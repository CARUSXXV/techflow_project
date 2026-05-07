# type: ignore
from odoo import models, fields, api


class TechRating(models.Model):
    _name = 'tech.rating'
    _description = 'Valoración de Equipo Tecnológico'
    _order = 'rating_date desc'

    # Nombre computado: "Equipo - Fecha"
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
        store=True
    )

    equipment_id = fields.Many2one(
        'tech.equipment',
        string='Equipo',
        required=True,
        ondelete='cascade'
    )

    evaluated_by_id = fields.Many2one(
        'res.users',
        string='Evaluado por',
        required=True,
        default=lambda self: self.env.user
    )

    rating_date = fields.Date(
        string='Fecha de Valoración',
        required=True,
        default=fields.Date.today
    )

    rating = fields.Selection([
        ('bad', 'Malo'),
        ('regular', 'Regular'),
        ('good', 'Bueno'),
        ('very_good', 'Muy Bueno'),
        ('excellent', 'Excelente'),
    ], string='Valoración', required=True)

    is_recommended = fields.Boolean(
        string='¿Recomendado?',
        compute='_compute_is_recommended',
        store=True
    )

    active = fields.Boolean(
        string='Activo',
        default=True
    )

    @api.depends('equipment_id', 'rating_date')
    def _compute_name(self):
        for rec in self:
            equip = rec.equipment_id.name or ''
            date = rec.rating_date or ''
            rec.name = f"{equip} - {date}" if equip or date else '/'

    @api.depends('rating')
    def _compute_is_recommended(self):
        for rec in self:
            rec.is_recommended = rec.rating == 'excellent'

    @api.onchange('rating')
    def _onchange_rating(self):
        self.is_recommended = self.rating == 'excellent'
