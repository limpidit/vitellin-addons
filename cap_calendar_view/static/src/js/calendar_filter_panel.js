/** @odoo-module **/

import { CalendarFilterPanel } from "@web/views/calendar/calendar_filter_panel";
import { onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CustomCalendarFilterPanel extends CalendarFilterPanel {
    setup() {
        super.setup();
        this.session = useService("session");

        onMounted(() => {
            const userId = this.session.uid;
            for (const section of this.props.model.filterSections) {
                const updates = {};
                for (const filter of section.filters) {
                    updates[filter.value] = (filter.value === userId);
                }
                this.props.model.updateFilters(section.fieldName, updates);
            }
        });
    }
}
