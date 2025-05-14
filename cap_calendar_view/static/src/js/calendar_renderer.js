/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CalendarSidebar } from "@web/views/calendar/calendar_sidebar";
import { useService } from "@web/core/utils/hooks";
import { onMounted } from "@odoo/owl";

patch(CalendarSidebar.prototype, {
    setup() {
        super.setup();
        this.user = useService("user");
        this.isFirstLoad = true;

        onMounted(() => {
            if (this.isFirstLoad) {
                this.isFirstLoad = false;
                this._uncheckAllFiltersExceptCurrentUser();
            }
        });
    },

    _uncheckAllFiltersExceptCurrentUser() {
        const userId = this.user.userId;
        const filters = this.props.sidebarState.filters;

        for (const filter of filters) {
            filter.active = false;
        }

        const userFilter = filters.find(f => f.value === userId);
        if (userFilter) {
            userFilter.active = true;
        }

        this.props.sidebarState.filters = [...filters]; // trigger reactive update
    },
});
