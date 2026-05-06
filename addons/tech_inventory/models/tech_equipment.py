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
    
    _sql_constraints = [
        ('serial_unique', 'unique(serial)', 'El número de serie debe ser único!')
    ]

    @api.constrains('serial')
    def _check_serial_length(self):
        for record in self:
            if record.serial and len(record.serial) < 8:
                raise ValidationError(_('El número de serie debe tener al menos 8 caracteres.'))

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




