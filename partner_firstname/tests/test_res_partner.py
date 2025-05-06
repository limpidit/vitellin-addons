
from odoo.addons.base.tests import test_res_partner
from odoo.tests import Form

def test_onchange_parent_sync_user(self):
    company_1 = self.env['res.company'].create({'name': 'company_1'})
    test_user = self.env['res.users'].create({
        'name': 'This user',
        'login': 'thisu',
        'email': 'this.user@example.com',
        'company_id': company_1.id,
        'company_ids': [company_1.id],
    })
    test_parent_partner = self.env['res.partner'].create({
        'company_type': 'company',
        'name': 'Micheline',
        'user_id': test_user.id,
    })
    with Form(self.env['res.partner']) as partner_form:
        partner_form.parent_id = test_parent_partner
        partner_form.company_type = 'person'
        partner_form.firstname = 'Philip'
        partner_form.lastname = 'K.'
        self.assertEqual(partner_form.user_id, test_parent_partner.user_id)

def test_lang_computation_form_view(self):
    """ Check computation of lang: coming from installed languages, forced
    default value and propagation from parent."""
    default_lang_info = self.env['res.lang'].get_installed()[0]
    default_lang_code = default_lang_info[0]
    self.assertNotEqual(default_lang_code, 'de_DE')  # should not be the case, just to ease test
    self.assertNotEqual(default_lang_code, 'fr_FR')  # should not be the case, just to ease test

    # default is installed lang
    partner_form = Form(self.env['res.partner'], 'base.view_partner_form')
    partner_form.firstname = "Test"
    partner_form.lastname = "Company"
    self.assertEqual(partner_form.lang, default_lang_code, "New partner's lang should be default one")
    partner = partner_form.save()
    self.assertEqual(partner.lang, default_lang_code)

    # check propagation of parent to child
    with partner_form.child_ids.new() as child:
        child.name = "First Child"
        self.assertEqual(child.lang, default_lang_code, "Child contact's lang should have the same as its parent")
    partner = partner_form.save()
    self.assertEqual(partner.child_ids.lang, default_lang_code)

    # activate another languages to test language propagation when being in multi-lang
    self.env['res.lang']._activate_lang('de_DE')
    self.env['res.lang']._activate_lang('fr_FR')

    # default from context > default from installed
    partner_form = Form(
        self.env['res.partner'].with_context(default_lang='de_DE'),
        'base.view_partner_form'
    )
    # <field name="is_company" invisible="1"/>
    # <field name="company_type" widget="radio" options="{'horizontal': true}"/>
    # @api.onchange('company_type')
    # def onchange_company_type(self):
    #     self.is_company = (self.company_type == 'company')
    partner_form.company_type = 'company'
    partner_form.firstname = "Test"
    partner_form.lastname = "Company"
    self.assertEqual(partner_form.lang, 'de_DE', "New partner's lang should take default from context")
    with partner_form.child_ids.new() as child:
        child.name = "First Child"
        self.assertEqual(child.lang, 'de_DE', "Child contact's lang should be the same as its parent.")
    partner_form.lang = 'fr_FR'
    self.assertEqual(partner_form.lang, 'fr_FR', "New partner's lang should take user input")
    with partner_form.child_ids.new() as child:
        child.name = "Second Child"
        self.assertEqual(child.lang, 'fr_FR', "Child contact's lang should be the same as its parent.")
    partner = partner_form.save()

    # check final values (kept from form input)
    self.assertEqual(partner.lang, 'fr_FR')
    self.assertEqual(partner.child_ids.filtered(lambda p: p.name == "First Child").lang, 'de_DE')
    self.assertEqual(partner.child_ids.filtered(lambda p: p.name == "Second Child").lang, 'fr_FR')

# Monkey patch des tests
test_res_partner.TestPartnerForm.test_onchange_parent_sync_user = test_onchange_parent_sync_user