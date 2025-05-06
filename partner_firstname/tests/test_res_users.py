
from odoo.addons.base.tests import test_res_users
from odoo.tests import Form

def patched_test_reified_groups(self):
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

def test_reified_groups_on_change(self):
    """Test that a change on a reified fields trigger the onchange of groups_id."""
    group_public = self.env.ref('base.group_public')
    group_portal = self.env.ref('base.group_portal')
    group_user = self.env.ref('base.group_user')

    # Build the reified group field name
    user_groups = group_public | group_portal | group_user
    user_groups_ids = [str(group_id) for group_id in sorted(user_groups.ids)]
    group_field_name = f"sel_groups_{'_'.join(user_groups_ids)}"

    # <group col="4" invisible="sel_groups_1_9_10 != 1" groups="base.group_no_one" class="o_label_nowrap">
    with self.debug_mode():
        user_form = Form(self.env['res.users'], view='base.view_users_form')

    user_form.firstname = "Test firstname"
    user_form.lastname = "Test lastname"
    user_form.login = "Test"
    self.assertFalse(user_form.share)

    user_form[group_field_name] = group_portal.id
    self.assertTrue(user_form.share, 'The groups_id onchange should have been triggered')

    user_form[group_field_name] = group_user.id
    self.assertFalse(user_form.share, 'The groups_id onchange should have been triggered')

    user_form[group_field_name] = group_public.id
    self.assertTrue(user_form.share, 'The groups_id onchange should have been triggered')

# Monkey patch du test directement
test_res_users.TestUsers2.test_reified_groups = patched_test_reified_groups
test_res_users.TestUsers2.test_reified_groups_on_change = test_reified_groups_on_change

