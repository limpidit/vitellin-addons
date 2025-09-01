from odoo import models
from datetime import timedelta, datetime, date
import logging

_logger = logging.getLogger(__name__)

class Tasks(models.Model):
    _inherit = 'project.task'

    def get_chantiers_sorted(self):
        """This function returns a list easily readable from an xml document
        the format of that list is [[user, date, [tasks], [isolant], [qty_isolant], nbre_spot], [..[][][].], [..[][][].]]
        """
        datas = []
        chantiers_sorted = self.filtered(lambda t: t.type_tache == 'chantier' and t.user_id and t.planned_date_begin).sorted(key=lambda t: (t.planned_date_begin))
        appendChantier = True
        index = 0

        "We go trhough all the project.task" \
        "  for this given task, we go through all the user_ids and all days of the task" \
        "    then we check if datas (the value we want to return) already has a value for a given user and date:" \
        "      if yes, then we only append the task list for this user and date," \
        "      if not, we append datas with a new list of user, date, [task]"
        for chantier in chantiers_sorted:
            dates_chantier = self.get_days(chantier)
            all_move_lines_isolant = chantier.mapped('chargement_ids.move_line_ids').filtered(lambda l: l.product_id.is_isolant)
            all_products_isolant = all_move_lines_isolant.mapped('product_id')
            total_qty=[]
            for isolant_product_id in all_products_isolant:
                total_qty.append(sum(all_move_lines_isolant.filtered(lambda l: l.product_id == isolant_product_id).mapped('chantier_quantite_a_charger')))

            for user in chantier.user_ids:
                for date in dates_chantier:
                    if len(datas) > 0:
                        for i in range(len(datas)):
                            if user in datas[i][0] and datas[i][1] == date.date():
                                appendChantier = True
                                index = i
                                break
                            else:
                                appendChantier = False
                        
                        if appendChantier:
                            datas[index][2].append(chantier)
                            if all_products_isolant in datas[index][3]:
                                _logger.info(f"here are our {datas}")
                                index_iso = datas[index][3].index(all_products_isolant)
                                _logger.info(f"here are our {datas[index]} index")
                                datas[index][4][index_iso][0] += total_qty[0]
                                
                            else:
                                datas[index][3].append(all_products_isolant)
                                datas[index][4].append(total_qty)
                        else:
                            datas.append([user, date.date(), [chantier], [all_products_isolant], [total_qty]])
                    else:
                        datas.append([user, date.date(), [chantier], [all_products_isolant], [total_qty]])
        return datas

    def get_days(self, chantiers):
        """This function returns the list of days for a given 'project.task'"""
        days = []
        count = 0
        for x in chantiers:
            count += 1
            begin_date = x.planned_date_begin
            while begin_date <= x.date_deadline:
                days.append(begin_date)
                begin_date = begin_date + timedelta(days=1)
        return days

