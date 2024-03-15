/**
 * Provides the callback for the modal popup
 *
 * @returns {object}    helper functions injected into view services
 */

var fxAppModalService = fxApp.factory('fxAppModalService', function() {

	var modalData = {
		alertTitle: '',
		alertMessage: '',
	};

	var defaultModalOptions = {
		showCancelButton: false,
		customButtons: [],
		response: ''
	};

	var modalOptions = {};

	function showModal(alertTitle, alertMessage, callback, options) {
		// set the modal data
		modalData.alertTitle = alertTitle;
		modalData.alertMessage = alertMessage;
		modalOptions = options ? options : defaultModalOptions;

		// show the modal
		$('#alertModal').modal('show');

		// remove the previously registered callback if there is one
		$('#alertModal').off('hidden.bs.modal');

		// register the new callback for when the modal is dismissed
		if (callback) {
			$('#alertModal').on('hidden.bs.modal', callback);
		}
	}

	function getModalData() {
		return modalData;
	}

	function getModalOptions() {
		return modalOptions;
	}

	function confirm(response) {
		modalOptions.response = response;
	}

    /**
     * Get the modal response
     * @returns {string}  response - The modal response
     */
    function getResponse() {
        return modalOptions.response;
    }

	return {
		getModalData: getModalData,
		getModalOptions: getModalOptions,
        getResponse: getResponse,
		showModal: showModal,
		confirm: confirm
	};
});

/**
 * Provides generic modals
 *
 * @returns {object} helper functions for creating modals
 */
var fxAppDialogService = fxApp.factory('fxAppDialogService',
	['$uibModal',
	function($uibModal) {

	function confirmDialog(modalOptions, okCallback) {
        var modalInstance = $uibModal.open({
            templateUrl: 'components/idioms/confirmDialog.html',
            controller: ['$scope', '$uibModalInstance', function($scope, $uibModalInstance) {
                $scope.modalOptions = modalOptions
                $scope.ok = function(result) {
                    $uibModalInstance.close(result);
                };
                $scope.cancel = function(result) {
                    $uibModalInstance.dismiss('cancel');
                };
            }
        ]});

        modalInstance.result.then(function (result) {
            okCallback();
        });
    }

    return {
        confirmDialog: confirmDialog
    };
}]);


/**
 * Provides the modal for performing filter queries
 *
 * @returns {object}    helper functions injected into view services
 */
var fxAppFilterService = fxApp.factory('fxAppFilterService',
	['fxAppViewService', '$uibModal',
	function(fxAppViewService, $uibModal) {

	var options = {};
	var clauses = [];
	var maxClauses = 10;
	var callback = function(clauses) {};
	var exportResults = function(){};
	var hasErrors = false;
	var modalInstance = {};

	/**
	 * Show the filter dialog
	 *
	 * @param   {object}    filterOptions - the options to choose from
	 * @param   {object}    okCallback - what happens when you click "OK"
	 */
	function showModal(filterOptions, okCallback) {
		// set the options
		if (filterOptions) {
			setOptions(filterOptions);
		}

		// set the callback
		if (okCallback) {
			setCallback(okCallback);
		}

		// show the modal
		modalInstance = $uibModal.open({
			animation: true,
			templateUrl: 'directives/fxFilterModal.html',
			windowTemplateUrl: 'directives/fxWideModal.html',
			controller: ['$scope', 'fxAppService', 'fxAppFilterService',
				function($scope, fxAppService, fxAppFilterService) {
					$scope.fxAppService = fxAppService;
					$scope.fxAppFilterService = fxAppFilterService;
				}
			]
		});
	}

	/**
	 * Hide the filter dialog
	 */
	function hideModal() {
		modalInstance.close();
	}

	/**
	 * Called when the object type is changed in a clause
	 *
	 * @param   {object}    clause - a single clause from the dialog
	 */
	function objectTypeChanged(clause) {
		var options = clause.options;
		var values = clause.values;
		values.field = Object.keys(options.criteria[values.objectType])[0];
	}

	/**
	 * Get the options for the selected object type and field
	 *
	 * @param   {object}    clause - a single clause from the dialog
	 * @returns {object}    the options
	 */
	function getFieldOptions(clause){
		var objectType = clause.values.objectType;
		var field = clause.values.field;
		var fieldOptions = clause.options.criteria[objectType][field];
		return fieldOptions;
	}

	/**
	 * Called when the field is changed in a clause
	 *
	 * @param   {object}    clause - a single clause from the dialog
	 */
	function fieldChanged(clause) {
		var fieldOptions = getFieldOptions(clause);

        // Mark the clause with the options so they can be referenced later
        clause.values.fieldOptions = fieldOptions;

		// set defaults values according to the options
		clause.values.exactMatch = fieldOptions.canBeExact;
		if (fieldOptions.type === 'Select') {
			clause.values.valueToMatch = fieldOptions.options[0];
			clause.values.minValue = '';
			clause.values.maxValue = '';
		}
		else if (fieldOptions.type === 'DateRange') {
			var now = moment();
			var minusFortnight = moment().subtract(2, 'weeks');
			var plusFortnight = moment().add(2, 'weeks');

			clause.values.valueToMatch = '';
			clause.values.minValue = fxAppViewService.ISOTimetoFXTime(minusFortnight.toISOString());
			clause.values.maxValue = fxAppViewService.ISOTimetoFXTime(plusFortnight.toISOString());
		}
		else {
			clause.values.valueToMatch = '';
			clause.values.minValue = '';
			clause.values.maxValue = '';
		}
	}

	/**
	 * Called when an additional clause needs to be added
	 *
	 * @param   {object}    clause - a single clause from the dialog
	 */
	function addClause() {
		if (canAddClause()) {
			// default values
			var values = {};
			values.enabled = true;
			values.clauseCondition = options.clauseCondition[0];
			values.objectType = Object.keys(options.criteria)[0];
			values.field = Object.keys(options.criteria[values.objectType])[0];
			values.valueToMatch = '';
			values.minValue = '';
			values.maxValue = '';
			values.exactMatch = false;
			values.incomplete = false;

			var clause = {options: options, values: values};

			// Handle date and select clauses also assign field options
			fieldChanged(clause);

			// add the clause
			clauses.push(clause);
		}
	}

	/**
	 * Called when a clause needs to be removed
	 *
	 * @param   {number}    index - index of a single clause from the dialog
	 */
	function removeClause(index) {
		// Check that we aren't removing the last clause
		if (index >= 0 && clauses.length > 1) {
			clauses.splice(index, 1);
		}
	}

	/**
	 * Called when the clauses need to be cleared out
	 */
	function clearClauses() {
		clauses = [];
		addClause();
	}

	/**
	 * Check the length of "clauses" to see if a clause can be added
	 *
	 * @returns {boolean}    whether a clause can be added
	 */
	function canAddClause() {
		return clauses.length < maxClauses;
	}

	/**
	 * Check that the form has been filled in correctly
	 *
	 * @param   {object}     clause - a single clause from the dialog
	 * @returns {boolean}    whether the form is incomplete or not
	 */
	function checkClausesForErrors() {
		// true if any clauses are incomplete
		var incomplete = false;

		// check if individual clauses are incomplete
		clauses.map(function(clause) {
			var fieldOptions = getFieldOptions(clause);

			if (fieldOptions.type === 'DateRange') {
				if (clause.values.minValue === '' || clause.values.maxValue === '') {
					incomplete = true;
					clause.values.incomplete = true;
				}
				else {
					clause.values.incomplete = false;
				}
			}
			else {
				if (clause.values.valueToMatch === '') {
					incomplete = true;
					clause.values.incomplete = true;
				}
				else {
					clause.values.incomplete = false;
				}
			}
		});

		return incomplete;
	}

	/**
	 * Get the array of clauses
	 *
	 * @param   {object}    clause - a single clause from the dialog
	 * @returns {array}     all the clauses in the dialog
	 */
	function getClauses() {
		return clauses;
	}

	/**
	 * Called when the user clicks "OK"
	 */
	function returnFilter() {
		callback(clauses);
	}

	/**
	 * Set the options available for the dialog
	 *
	 * @param   {object}    filterOptions - the options
	 */
	function setOptions(filterOptions) {
		// clear the clauses if the options changed
		var shouldClear = !angular.equals(options, filterOptions);

		// set the filter options
		options = filterOptions;

		if (shouldClear) {
			clearClauses();
		}
	}

	/**
	 * Get the options
	 *
	 * @returns   {object}    the options
	 */
	function getOptions() {
		return options;
	}

	/**
	 * Set the callback
	 *
	 * @param   {object}    okCallback - what happens when you click "OK"
	 */
	function setCallback(okCallback) {
		// wrap the callback given
		callback = function(clauses) {
			// perform basic validation
			if (!checkClausesForErrors()) {
				// call the callback
				okCallback(clauses, function() {
					// close the modal
					hideModal();
				});
            } else {
                // clear the filter clauses
                clearClauses();
            }
		};
	}

    /**
     * Check if exact should be disabled
     * @params {object}  clause - the clause to check for
     * @returns {boolean}  True if it should be disabled false otherwise
     */
    function disableExact(clause) {
        var fieldOptions = getFieldOptions(clause);
        return !fieldOptions.canBeExact || fieldOptions.type === 'ExactText';

    }

	return {
		addClause: addClause,
        disableExact: disableExact,
		removeClause: removeClause,
		clearClauses: clearClauses,
		canAddClause: canAddClause,
		getClauses: getClauses,
		objectTypeChanged: objectTypeChanged,
		fieldChanged: fieldChanged,
		showModal: showModal,
		hideModal: hideModal,
		setOptions: setOptions,
		getOptions: getOptions,
		setCallback: setCallback,
		returnFilter: returnFilter,
		exportResults: exportResults
	};
}]);
