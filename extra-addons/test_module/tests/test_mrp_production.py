# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError

# TODO: 

class MRPTest(TransactionCase):
    """This class is a representation for unit test for the model mrp.production

        Tests:
          - test_create_mrp_production_as_mrp_user: Checks if a user with access
            rights can create a record
          - test_create_mrp_production_as_employee: Checks if a user with no 
            access rights cannot create a record
            
            Note:
            In the objects that require a relationship to product.template
            (product.product and mrp.bom) asign them as follows:
                - product_product.product_tmpl_id = false (line 140)
                - mrp_bom.product_tmpl_id = product_template_id.id (line 182)
            otherwise it will not work 
    """

    def setUp(self, *args, **kwargs):
        super(MRPTest, self).setUp(*args, **kwargs)
        # References
        product_product_ref = self.env['product.product']
        product_template_ref = self.env['product.template']
        product_categ_ref = self.env.ref('product.product_category_all')
        product_uom_ref = self.env['product.uom']
        product_uom_categ_ref = self.env['product.uom.categ']
        ir_sequence_ref = self.env['ir.sequence']
        stock_picking_type_ref = self.env['stock.picking.type']
        stock_location_ref = self.env['stock.location']
        mrp_bom_ref = self.env['mrp.bom']

        # Initial objects	
        company_id = self.env['res.company'].search([], limit=1)
        product_uom_categ_id = product_uom_categ_ref.create(
            {'name': 'product_uom_unit_test'}
        )
        stock_location_id = stock_location_ref.create({
            'usage': 'supplier',
            'name': 'stock_location_unit_test',
        })
        self.public_user_id = self.env.ref('base.public_user')
        self.public_user_id.partner_id.write( {'email': 'demo@domain.com'} )

        # product.uom dictionary
        product_uom_dict = {
            'uom_type': 'bigger',
            'rounding': 1.0000,
            'name': 'product_uom_unit_test',
            'factor': 1.0000,
            'factor_inv': 1.0000,
            'category_id': product_uom_categ_id.id,
        }
        product_uom_id = product_uom_ref.create(product_uom_dict)


        # Prodyct.category dictionary
        product_category_dict = {
            'property_valuation': 'manual_periodic',
            'property_cost_method': 'standard',
            'name': 'product_category_unit_test',
        }
        product_category_id = product_categ_ref.create(product_category_dict)

        # Product.template dictionary
        product_template_dict = {
            'product_variant_ids': [(6, False, [])],
            'name': 'tmp_product',
            'type': 'consu',
            'sale_line_warn': 'no-message',
            'uom_id': product_uom_id.id,
            'uom_po_id': product_uom_id.id,
            'categ_id': product_category_id.id,
            'tracking': 'none',
            
        }
        product_template_id = product_template_ref.create(product_template_dict)

        # Product.product dictionary
        product_product_dict = {
            'product_variant_ids': [(6, False, [])],
            'product_tmpl_id': False,
            'name': 'tmp_product',
            'categ_id': product_category_id.id,

            'uom_po_id': product_uom_id.id,
            'uom_id': product_uom_id.id,
            'type': 'consu',
            'tracking': 'none',
            'sale_line_warn': 'no-message',
        }
        product_product_id = product_product_ref.create(product_product_dict)
        
        # ir.sequence dictionary
        ir_sequence_dict = {
            'name': 'ir_sequence_unit_test',
            'padding': 10,
            'number_next': 1,
            'number_increment': 1,
            'implementation': 'standard',
        }
        ir_sequence_id = ir_sequence_ref.create(ir_sequence_dict)

        # stock.picking.type dictionary
        stock_picking_type_dict = {
            'code': 'incoming',
            'sequence_id': ir_sequence_id.id,
            'name': 'stock_picking_type_unit_test',

        }
        stock_picking_type_id = stock_picking_type_ref.create(
            stock_picking_type_dict
        )

        # mrp.bom dictionary
        mrp_bom_dict = {
            'product_qty': 1.000,
            'company_id': company_id.id,
            'product_uom_id': product_uom_id.id,
            'product_tmpl_id': product_template_id.id,
            'type': 'normal',
            'ready_to_produce': 'all_available',
        }
        mrp_bom_id = mrp_bom_ref.create(mrp_bom_dict)


        # mrp.production dict
        self.mrp_production_dict = {
            'product_uom_id' : product_uom_id.id,
            'product_qty': 1.00000,
            'company_id': company_id.id,
            'product_id': product_product_id.id,
            'picking_type_id': stock_picking_type_id.id,
            'location_src_id': stock_location_id.id,
            'location_dest_id': stock_location_id.id,
            'date_planned_start': datetime.now(),
            'bom_id': mrp_bom_id.id,
        }


    def test_create_mrp_production_as_mrp_user(self):
        """ Checks if a user with access rights can create a mrp.production """
        # Add the public user to the mrp.group_mrp_user group
        self.env.ref('mrp.group_mrp_user').write({
            'users': [(4, self.public_user_id.id, False)],
        })
        # Create a new ref with the public user
        mrp_production_ref = self.env['mrp.production'].sudo(
            self.public_user_id
        )
        try:
            mrp_production_obj = mrp_production_ref.create(
                self.mrp_production_dict
            )
        except AccessError as e:
            self.fail("This user cannot create an mrp.production object\
                due to acces rights")

    def test_create_mrp_production_as_employee(self):
        """ Checks if an employee cannot create a mrp.production """
        # Add the user to the employee group
        self.env.ref('base.group_user').write({
            'users': [(4, self.public_user_id.id, False)]
        })
        # get a reference with the public user
        mrp_production_ref = self.env['mrp.production'].sudo(
            self.public_user_id
        )
        with self.assertRaises(AccessError):
            mrp_production_obj = mrp_production_ref.create(
                self.mrp_production_dict
            )