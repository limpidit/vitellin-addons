odoo.define('cap_industry_fsm.MapRenderer', [
    'web.core',
    'web_map.MapRenderer'
], function (core, MapRenderer) {
    'use strict';

    var qweb = core.qweb;

    MapRenderer.include({

        /**
         * METHODE SURCHARGEE pour introduire une coloration du "marker" en fonction de la planification de la tâche
         *
         * If there's located records, adds the corresponding marker on the map
         * Binds events to the created markers
         * @private
         * @param {Array} records array that contains the records that needs to be displayed on the map
         * @param {Object} records.partner is the partner linked to the record
         * @param {float} records.partner.partner_latitude latitude of the partner and thus of the record
         * @param {float} records.partner.partner_longitude longitude of the partner and thus of the record
         */
        _addMakers: function (records) {
            var self = this;
            this._removeMakers();
            records.forEach(function (record) {
                if (record.partner && record.partner.partner_latitude && record.partner.partner_longitude) {
                    var popup = {};
                    popup.records = self._getMarkerPopupFields(record, self.fieldsMarkerPopup);
                    popup.url = 'https://www.google.com/maps/dir/?api=1&destination=' +
                        record.partner.partner_latitude + ',' +
                        record.partner.partner_longitude;

                    var $popup = $(qweb.render('map-popup', { records: popup }));
                    var openButton = $popup.find('button.btn.btn-primary.edit')[0];
                    if (self.hasFormView) {
                        openButton.onclick = function () {
                            self.trigger_up('open_clicked', { id: record.id });
                        };
                    } else {
                        openButton.remove();
                    }

                    var marker;
                    var offset;

                    if (self.numbering) {
                        let color_class = 'marker_orange';
                        if (record.numero_semaine && record.user_id) {
                            color_class = 'marker_blue';
                        }

                        var number = L.divIcon({
                            className: 'o_numbered_marker ' + color_class,
                            html: '<p class="o_number_icon">' + (self.state.records.indexOf(record) + 1) + '</p>',
                        });
                        marker = L.marker([record.partner.partner_latitude, record.partner.partner_longitude], { icon: number });
                        offset = new L.Point(0, -35);
                    } else {
                        marker = L.marker([record.partner.partner_latitude, record.partner.partner_longitude]);
                        offset = new L.Point(0, 0);
                    }

                    marker.addTo(self.leafletMap).bindPopup(function () {
                        var divPopup = document.createElement('div');
                        $popup.each(function (i, element) {
                            divPopup.appendChild(element);
                        });
                        return divPopup;
                    }, { offset: offset });

                    self.markers.push(marker);
                }
            });
        },
    });

    return MapRenderer;
});
