# type: ignore
from odoo import models, fields, api, _
# type: ignore
from odoo.exceptions import ValidationError

class TechEquipment(models.Model):
    _name = 'tech.equipment'
    _description = 'Equipo Tecnológico'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(string='Nombre del Equipo', required=True)
    serial = fields.Char(
        string='Número de Serie', 
        required=True, 
        unique=True,
        index=True
    )
    
    category_id = fields.Many2one(
        'tech.category', 
        string='Categoría',
        required=True,
        ondelete='restrict'
    )
    
    employee_id = fields.Many2one(
        'hr.employee', 
        string='Empleado Asignado',
    )
    
    state = fields.Selection([
        ('available', 'Disponible'),
        ('assigned', 'Asignado'),
        ('repair', 'En Reparación'),
        ('decommissioned', 'Desincorporado')
    ], string='Estado', required=True, default='available')
    
    cost = fields.Monetary(
        string='Costo (USD)', 
        currency_field='currency_id',
        required=True
    )
    
    tax_value = fields.Monetary(
        string='Valor con Impuesto (15%)',
        compute='_compute_tax_value',
        store=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency', 
        default=lambda self: self.env.company.currency_id
    )
    
    notes = fields.Text(string='Notas Adicionales')
    purchase_date = fields.Date(string='Fecha de Compra')
    
    rating_ids = fields.One2many(
        'tech.rating', 
        'equipment_id', 
        string='Valoraciones'
    )
    
    rating_count = fields.Integer(
        string='Cantidad de Valoraciones',
        compute='_compute_rating_count'
    )

    _sql_constraints = [
        ('serial_unique', 'unique(serial)', 'El número de serie debe ser único!')
    ]

    @api.constrains('purchase_date')
    def _check_purchase_date(self):
        for record in self:
            if record.purchase_date and record.purchase_date > fields.Date.today():
                raise ValidationError(_('La fecha de compra no puede ser una fecha futura.'))

    @api.onchange('purchase_date')
    def _onchange_purchase_date(self):
        if self.purchase_date and self.purchase_date > fields.Date.today():
            return {
                'warning': {
                    'title': _("Fecha Inválida"),
                    'message': _("La fecha de compra no puede ser una fecha futura."),
                }
            }

    @api.constrains('serial')
    def _check_serial_length(self):
        for record in self:
            if record.serial and len(record.serial) < 8:
                raise ValidationError(_('El número de serie debe tener al menos 8 caracteres.'))

    @api.depends('rating_ids')
    def _compute_rating_count(self):
        for record in self:
            record.rating_count = len(record.rating_ids)

    @api.depends('cost')
    def _compute_tax_value(self):
        for record in self:
            record.tax_value = record.cost * 1.15

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.state = 'assigned'

    def action_set_repair(self):
        self.write({
            'state': 'repair',
            'employee_id': False
        })

    def action_set_decommissioned(self):
        self.write({
            'state': 'decommissioned',
            'employee_id': False
        })

    def action_set_available(self):
        self.write({
            'state': 'available',
            'employee_id': False
        })

    def action_add_rating(self):
        self.ensure_one()
        return {
            'name': _('Nueva Valoración'),
            'type': 'ir.actions.act_window',
            'res_model': 'tech.rating',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_equipment_id': self.id,
                'default_evaluated_by_id': self.env.user.id,
            }
        }

    def action_view_ratings(self):
        self.ensure_one()
        return {
            'name': _('Valoraciones del Equipo'),
            'type': 'ir.actions.act_window',
            'res_model': 'tech.rating',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }




