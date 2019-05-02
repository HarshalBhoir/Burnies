odoo.define('pragtech_crm_activity.ActivityRenderer', function (require) {
	"use strict";
	
	var ActivityRenderer = require('mail.ActivityRenderer');
	var core = require('web.core');
	var field_registry = require('web.field_registry');

	var QWeb = core.qweb;
	var _t = core._t;
	ActivityRenderer.include({
		//Inherited to add Column Header
		/**
	     * @private
	     * @returns {jQueryElement} a jquery element <thead>
	     */
	    _renderHeader: function () {
	        var $tr = $('<tr>')
	                .append($('<th>').html('Opportunity').addClass("o_activity_type_cell"))
	                .append($('<th>').html('Customer').addClass("o_activity_type_cell"))
	                .append(_.map(this.state.data.activity_types, this._renderHeaderCell.bind(this)));
	        return $('<thead>').append($tr);
	    },
	    //Inherited to add Customer Column and Timestamp to date
	    /**
	     * @private
	     * @param {Object} data
	     * @returns {jQueryElement} a <tr> element
	     */
	    _renderRow: function (data) {
	        var self = this;
	        var res_id = data[0];
	        var name = data[1];
	        var customer = data[2];
	        var $nameTD = $('<td>')
	            .addClass("o_res_name_cell")
	            .html(name)
	            .data('res-id', res_id);
	        //Partner Name
	        var $partnerNameTD = $('<td>')
            .addClass("o_partner_name_cell")
            .html(customer);
	        var $cells = _.map(this.state.data.activity_types, function (node) {
	            var $td = $('<td>').addClass("o_activity_summary_cell");
	            var activity_type_id = node[0];
	            var activity_group = self.state.data.grouped_activities[res_id][activity_type_id];
	            activity_group = activity_group || {count: 0, ids: [], state: false};
	            if (activity_group.state) {
	                $td.addClass(activity_group.state);
	            }
	            // we need to create a fake record in order to instanciate the KanbanActivity
	            // this is the minimal information in order to make it work
	            // AAB: move this to a function
	            var record = {
	                data: {
	                    activity_ids: {
	                        model: 'mail.activity',
	                        res_ids: activity_group.ids,
	                    },
	                    activity_state: activity_group.state,
	                },
	                fields: {
	                    activity_ids: {},
	                    activity_state: {
	                        selection: [
	                            ['overdue', "Overdue"],
	                            ['today', "Today"],
	                            ['planned', "Planned"],
	                        ],
	                    },
	                },
	                fieldsInfo: {},
	                model: self.state.data.model,
	                ref: res_id, // not necessary, i think
	                type: 'record',
	                res_id: res_id,
	                getContext: function () {
	                    return {}; // session.user_context
	                },
	                //todo intercept event or changes on record to update view
	            };
	            var KanbanActivity = field_registry.get('kanban_activity');
	            var widget = new KanbanActivity(self, "activity_ids", record, {});
	            widget.appendTo($td);
	            // replace clock by closest deadline
	            var $date = $('<div>');
	            var formated_date = moment(activity_group.o_closest_deadline).format('lll');
	            var current_year = (new Date()).getFullYear();
	            if (formated_date.includes(current_year)) { // Dummy logic to remove year (only if current year), we will maybe need to improve it
	            	formated_date = formated_date.replace(current_year,'')
	                formated_date = formated_date.replace(/( |,)*$/g, "");
	            }
	            $date
	                .text(formated_date)
	                .addClass('o_closest_deadline');
	            $td.find('a')
	                .empty()
	                .append($date);
	            return $td;
	        });
	        var $tr = $('<tr/>', {class: 'o_data_row'})
	            .append($nameTD)
	            .append($partnerNameTD)
	            .append($cells);
	        return $tr;
	    },
	});
	
});