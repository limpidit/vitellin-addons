odoo.define('cap_calendar_attendees.CalendarModel', function (require) {
"use strict";

var AbstractModel = require('web.AbstractModel');
var Context = require('web.Context');
var core = require('web.core');
var fieldUtils = require('web.field_utils');
var CalendarModel = require('web.CalendarModel');

var _t = core._t;

CalendarModel.include({
    _loadCalendar: function () {
        var self = this;
        this.data.fc_options = this._getFullCalendarOptions();


        var str=[]
        var dom_len = self._getFilterDomain().length
        if (dom_len == 2)
            str = ['|']
        if (dom_len == 3)
            str = ['|','|']

        var domain = self.data.domain.concat('&').concat(self._getRangeDomain()).concat(str).concat(self._getFilterDomain())
        console.log(domain)
        var defs = _.map(this.data.filters, this._loadFilter.bind(this));
        return Promise.all(defs).then(function () {
            return self._rpc({
                    model: self.modelName,
                    method: 'search_read',
                    context: self.data.context,
                    fields: self.fieldNames,
                    domain: domain
            })
            .then(function (events) {
                self._parseServerData(events);
                self.data.data = _.map(events, self._recordToCalendarEvent.bind(self));
                return Promise.all([
                    self._loadColors(self.data, self.data.data),
                    self._loadRecordsToFilters(self.data, self.data.data)
                ]);
            });
        });
    },
});

});