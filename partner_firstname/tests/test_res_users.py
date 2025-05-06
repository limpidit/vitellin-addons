
from odoo.addons.base.tests.test_res_users import TestUsers2
from odoo.tests.common import tagged
from odoo.tests import Form


@tagged('standard', '-at_install')
class TestUsers2Patched(TestUsers2):

    def test_reified_groups(self):
        """ The groups handler doesn't use the "real" view with pseudo-fields
        during installation, so it always works (because it uses the normal
        groups_id field).
        """
        # use the specific views which has the pseudo-fields
        f = Form(self.env['res.users'], view='base.view_users_form')
        f.firstname = "bob"
        f.lastname = "test"
        f.login = "bob"
        user = f.save()

        self.assertIn(self.env.ref('base.group_user'), user.groups_id)

        # all template user groups are copied
        default_user = self.env.ref('base.default_user')
        self.assertEqual(default_user.groups_id, user.groups_id)
