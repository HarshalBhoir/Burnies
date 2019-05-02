odoo.define('pragtech_crm_activity.Activity', function(require) {
	"use strict";
	var core = require('web.core');
	var time = require('web.time');
	var QWeb = core.qweb;
	var _t = core._t;
	var BasicModel = require('web.BasicModel');
	
	//New Function to replace _readActivities function and convert datetime_deadline to moments 
	function _readAllActivities(self, ids) {
	    if (!ids.length) {
	        return $.when([]);
	    }
	    return self._rpc({
	        model: 'mail.activity',
	        method: 'activity_format',
	        args: [ids],
	        context: (self.record && self.record.getContext()) || self.getSession().user_context,
	    }).then(function (activities) {
	        // convert create_date and date_deadline to moments
	        _.each(activities, function (activity) {
	            activity.create_date = moment(time.auto_str_to_date(activity.create_date));
	            activity.date_deadline = moment(time.auto_str_to_date(activity.date_deadline));
	            //Ad
	            activity.datetime_deadline = moment(time.auto_str_to_date(activity.datetime_deadline));
	        });
	         // sort activities by due date
	        activities = _.sortBy(activities, 'date_deadline');
	        return activities;
	    });
	}
	
	//Inherted to replace _readActivities function call with _readAllActivities function
	BasicModel.include({
	    //--------------------------------------------------------------------------
	    // Private
	    //--------------------------------------------------------------------------

	    /**
	     * Fetches the activities displayed by the activity field widget in form
	     * views.
	     *
	     * @private
	     * @param {Object} record - an element from the localData
	     * @param {string} fieldName
	     * @return {Deferred<Array>} resolved with the activities
	     */
	    _fetchSpecialActivity: function (record, fieldName) {
	        var localID = (record._changes && fieldName in record._changes) ?
	                        record._changes[fieldName] :
	                        record.data[fieldName];
	        return _readAllActivities(this, this.localData[localID].res_ids);
	    },
	});
});