/**
 * Provides commonly used functions for the widgets
 *
 * @returns {object}    helper functions injected into the widgets
 */
var fxWidgets = fxApp.factory('fxWidgets', ['$timeout', function($timeout) {

	/**
	 * Pushes an event onto the end of the call queue
	 * Useful when you need to call functions in a particular order
	 *
	 * @param {function}    function to be called at the end of the current call queue
	 */
	function enqueueEvent(callback) {
		$timeout(function() { callback(); }, 0);
	}

	return {
		enqueueEvent: enqueueEvent
	};
}]);

/**
 * fx-button
 * ---------
 * callbacks: callback
 * attrs: type, size, innerstyle, disabled, callback
 * 
 * Bootstrap buttons
 */
var fxButtonTypes = { 
	noType:  { name: 'noType',  class: 'default', width: '',      size: 'md' },
	default: { name: 'default', class: 'default', width: 'block', size: 'md' },
	primary: { name: 'primary', class: 'primary', width: 'block', size: 'md' },
	success: { name: 'success', class: 'success', width: 'block', size: 'md' },
	info:    { name: 'info',    class: 'info',    width: 'block', size: 'md' },
	danger:  { name: 'danger',  class: 'danger',  width: 'block', size: 'md' },
	warning: { name: 'warning', class: 'warning', width: 'block', size: 'md' }
};

var fxButton = fxApp.component('fxButton', {
	templateUrl: 'directives/fxButton.html',
	transclude: true,
	bindings: {
		type: '@',
		size: '@',
		innerstyle: '@',
		disabled: '@',
		callback: '='
	},
	controller: ['$scope', '$attrs', function($scope, $attrs) {
		$scope.typeObj = $attrs.type ? fxButtonTypes[$attrs.type] : fxButtonTypes['noType'];
	}]
});

/**
 * fx-select-obj
 * -------------
 * callbacks: (none)
 * attrs: label, disabled, options, selected
 * 
 * Useful when you have an iterable object where the value is displayed
 * and the key is what you select
 */
var fxSelectObj = fxApp.component('fxSelectObj', {
	templateUrl: 'directives/fxSelectObj.html',
	bindings: {
		label: '@',
		required: '@',
		disabled: '@',
        buttonClasses: '@',
		options: '<',
		selected: '='
	},
	controller: ['$scope', function($scope) {
		$scope.ctrl = this;
		$scope.selectedFilter = function(id) {
			return $scope.ctrl.options[Object.keys($scope.ctrl.options).filter(function(option) {
				return option === id;
			})[0]];
		};
	}]
});

/**
 * fx-select-nested-obj
 * -------------
 * callbacks: (none)
 * attrs: label, disabled, options, selected
 * 
 * Useful when you have an iterable object where the value is displayed
 * and the key is what you select
 */
var fxSelectNestedObj = fxApp.component('fxSelectNestedObj', {
    templateUrl: 'directives/fxSelectNestedObj.html',
    bindings: {
        label: '@',
        required: '@',
        disabled: '@',
        buttonClasses: '@',
        nestedOptions: '<',
        selected: '='
    },
    controller: ['$scope', function($scope) {
        $scope.ctrl = this;
        $scope.selectedFilter = function(id) {

            for (var i = 0; i < $scope.ctrl.nestedOptions.length; ++i) {
                var item = $scope.ctrl.nestedOptions[i];
                if (item.id === id) {
                    return item.name;
                }
                
                for (var j = 0; j < item.children.length; ++j) {
                    var child = item.children[j];
                    if (id === child.id) {
                        return child.name;
                    }
                }
            }
        };
    }]
});

/**
 * fx-select-obj-2
 * ---------------
 * callbacks: (none)
 * attrs: label, required, disabled, options, groupmode, selected
 * 
 * Useful when you have an iterable object where the key is displayed
 * and the key and value are what you select (must use the 'form-control'
 * class on transcluded item if in group mode)
 */
var fxSelectObj2 = fxApp.component('fxSelectObj2', {
	templateUrl: 'directives/fxSelectObj2.html',
	transclude: true,
	bindings: {
		label: '@',
		required: '@',
		disabled: '@',
		options: '<',
		groupmode: '@',
		selected: '='
	},
	controller: ['$scope', function($scope) {
		$scope.ctrl = this;
		$scope.selectedPair = function(k, v) {
			if (k && v){
				var obj = {};
				obj[k] = v;
				return obj;
			}
			else {
				return {};
			}
		};
		$scope.getKey = function(obj) {
			return obj ? Object.keys(obj)[0] : "Select an item";
		};
	}]
});

/**
 * fx-select-arr
 * -------------
 * callbacks: (none)
 * attrs: label, disabled, options, groupmode, selected
 * 
 * Useful when you have an array of strings
 */
var fxSelectArr = fxApp.component('fxSelectArr', {
	templateUrl: 'directives/fxSelectArr.html',
	transclude: true,
	bindings: {
		label: '@',
		required: '@',
		disabled: '@',
		options: '<',
		groupmode: '@',
		selected: '=',
        buttoncls: '@'
	}
});

/**
 * fx-select-arr-obj
 * -----------------
 * callbacks: onselected
 * attrs: onselected, label, required, disabled, options, optionlabel, groupmode, selected
 * 
 * Useful when you have an array of objects and you want to choose a particular
 * key from the selected object whose value is the display name (optionlabel)
 */
var fxSelectArrObj = fxApp.component('fxSelectArrObj', {
	templateUrl: 'directives/fxSelectArrObj.html',
	transclude: true,
	bindings: {
		onselected: '&',
		label: '@',
		required: '@',
		disabled: '@',
		options: '<',
		optionlabel: '@',
		groupmode: '@',
		selected: '='
	},
	controller: ['$scope', '$parse', function($scope, $parse){
		$scope.ctrl = this;
		$scope.ctrl.callback = $scope.ctrl.onselected();

		$scope.resolveOptionLabel = function(option){
			var context = { option: option };
			return $parse('option.' + $scope.ctrl.optionlabel)(context);
		};
	}]
});

/**
 * fx-select-multiple
 * ------------------
 * callbacks: (none)
 * attrs: label, iconclass, placeholder, disabled, options, selected
 * 
 * For selecting multiple items from a set of options
 */
var fxSelectMultiple = fxApp.component('fxSelectMultiple', {
	templateUrl: 'directives/fxSelectMultiple.html',
	bindings: {
		label: '@',
		iconclass: '@',
		placeholder: '@',
		disabled: '@',
		options: '<',
		selectedContainer: '='
	},
	controller: ['$scope', 'fxWidgets', function($scope, fxWidgets) {
		$scope.ctrl = this;

		// init
		fxWidgets.enqueueEvent(function() {
			$('.select2').select2({ width: '100%', closeOnSelect: false });
		});

		// update when data changes
		$scope.$watch('ctrl.selectedContainer.selected',function() {
			fxWidgets.enqueueEvent(function() {
				$('.select2').select2({ width: '100%', closeOnSelect: false });
			});
		});
	}]
});

/**
 * fx-date
 * -------
 * callbacks: (none)
 * attrs: label, maxdate, required, disabled, datestring
 * 
 * For picking a date
 */
var fxDate = fxApp.component('fxDate', {
	templateUrl: 'directives/fxDate.html',
	bindings: {
		label: '@',
		maxdate: '@',
		required: '@',
		disabled: '@',
		datestring: '='
	},
	controller: ['$scope', 'fxWidgets', function($scope, fxWidgets) {
		$scope.ctrl = this;

		// set the date string the plugin uses
		$scope.ctrl.plugin = {
			datestring: toWidgetFormat($scope.ctrl.datestring)
		};

		// update the date string in the form data
		$scope.updateFormData = function(){
			$scope.ctrl.datestring = fromWidgetFormat($scope.ctrl.plugin.datestring);
		};

		// cache the time so we can add it back later
		var midnightHour = " 00:00:00";

		function removeTime(timeStr) {
			var timeRegex = /.{3}:.{2}:.{2}/g;
			midnightHour = timeRegex.exec(timeStr)[0];
			return timeStr.replace(timeRegex, '');
		}

		function addTime(timeStr) {
			return timeStr + midnightHour;
		}

		function replaceSlashWithDash(timeStr) {
			return timeStr.replace(/[\/]/g, '-');
		}

		function replaceDashWithSlash(timeStr) {
			return timeStr.replace(/[-]/g, '/');
		}

		function toWidgetFormat(timeStr) {
			var formattedTime = removeTime(replaceDashWithSlash(timeStr));
			var groups = /(.+)\/(.+)\/(.+)/g.exec(formattedTime);
			var year = groups[1];
			var month = groups[2];
			var day = groups[3];

			return month + "/" + day + "/" + year;
		}

		function fromWidgetFormat(timeStr) {
			var formattedTime = replaceSlashWithDash(timeStr);
			var groups = /(.+)-(.+)-(.+)/g.exec(formattedTime);
			var month = groups[1];
			var day = groups[2];
			var year = groups[3];

			return addTime(year + "-" + month + "-" + day);
		}

		fxWidgets.enqueueEvent(function() {
			$('.daterange').daterangepicker({
				singleDatePicker: true,
				showDropdowns: true,
				maxDate: $scope.ctrl.maxdate ? toWidgetFormat($scope.ctrl.maxdate) : undefined
			});
		});
	}]
});

/**
 * fx-date-time
 * ------------
 * callbacks: (none)
 * attrs: label, maxdate, disabled, datestring
 * 
 * For picking a date and time
 */
var fxDateTime = fxApp.component('fxDateTime', {
	templateUrl: 'directives/fxDateTime.html',
	bindings: {
		label: '@',
		maxdate: '@',
		disabled: '@',
		datestring: '='
	},
	controller: ['$scope', 'fxWidgets', function($scope, fxWidgets) {
		$scope.ctrl = this;

		fxWidgets.enqueueEvent(function() {
			$('.datetimepicker').datetimepicker({
				format: 'yyyy-mm-dd hh:ii:ss',
				showMeridian: true,
				endDate: $scope.ctrl.maxdate,
				timezone: 'UTC'
			});
		});
	}]
});

/**
 * fx-date-range
 * -------------
 * callbacks: (none)
 * attrs: label, datestring
 * 
 * For picking a start and end date
 */
var fxDateRange = fxApp.component('fxDateRange', {
	templateUrl: 'directives/fxDateRange.html',
	bindings: {
		label: '@',
		datestring: '='
	},
	controller: ['$scope', 'fxWidgets', function($scope, fxWidgets) {
		$scope.ctrl = this;
		fxWidgets.enqueueEvent(function() {
			$('.daterange').daterangepicker();
		});
	}]
});

/**
 * fx-input
 * --------
 * callbacks: (none)
 * attrs: label, iconclass, type, required, disabled, autofocus, value
 * 
 * For entering text
 */
var fxInput = fxApp.component('fxInput', {
	templateUrl: 'directives/fxInput.html',
	bindings: {
		label: '@',
		iconclass: '@',
		type: '@',
		required: '@',
		disabled: '@',
		autofocus: '@',
		value: '='
	}
});

/**
 * fx-input-mask
 * -------------
 * callbacks: (none)
 * attrs: label, iconclass, mask, disabled, csvregex, forceregex, regex, restrict, whenBlurred, value
 * 
 * For entering text with a format enforced
 */
var fxInputMask = fxApp.component('fxInputMask', {
	templateUrl: 'directives/fxInputMask.html',
	bindings: {
		label: '@',
		iconclass: '@',
		mask: '@',
		disabled: '@',
		regex: '@',
		csvregex: '@',
		forceregex: '@',
		restrict: '@',
        required: '@',
        whenblurred: '&',
        value: '=',
        formInvalid: '=?',
	},
	controller: ['$scope', 'fxWidgets', 'fxAppStringService',
		function($scope, fxWidgets, fxAppStringService) {

		$scope.ctrl = this;

        if (this.formInvalid === undefined) {
            this.formInvalid = false;
        }

		// Used when regex is true
		var mask = {};
		var restrict = {};
        updateInvalid(false);

		// Init
		fxWidgets.enqueueEvent(function() {
			$scope.blurCallback = $scope.ctrl.whenblurred();

			if ($scope.ctrl.regex === 'true') {
				mask = new RegExp($scope.ctrl.mask ? $scope.ctrl.mask : '', 'g');
				restrict = new RegExp($scope.ctrl.restrict ? $scope.ctrl.restrict : '', 'g');
				$scope.checkRegexInput();
			}
			else {
				$(':input[data-inputmask-mask]').inputmask({ 'clearIncomplete': true });
			}
		});

		// Validate the input against a regular expression
		function getValidInput(str, regex) {
			// Determine whether to interpret the string as CSV and validate
			// each item, or just validate the the raw string
			if ($scope.ctrl.csvregex === 'true') {
				return fxAppStringService.regexForCSV(str, regex) ? str : '';
			}
			else {
				var results = str.match(regex);

				if (results) {
					return results[0] === str ? str : '';
				}

				return '';
			}
		}

		// Remove restricted characters
		function sanitizeInput(str, regex) {
			if (str) { 
				return str.replace(regex, '');
			}
			else {
				return '';
			}
		}

        function updateInvalid(val) {
            $scope.invalid = val;
            $scope.ctrl.formInvalid = $scope.invalid;

            // Do not let submit if required
            if ($scope.ctrl.value === '' && $scope.ctrl.required) {
                $scope.ctrl.formInvalid = true;
            }
        }

		// Cache the last valid input
		$scope.lastValidStr = '';
		$scope.checkRegexInput = function() {
			$scope.ctrl.value = sanitizeInput($scope.ctrl.value, restrict);
			var result = getValidInput($scope.ctrl.value, mask);

            updateInvalid(result === '' && $scope.ctrl.value !== '');

			// Allow the user to clear out the field
			if ($scope.ctrl.value) {
				// If the input was invalid, do not cache the result
				$scope.lastValidStr = result ? result : $scope.lastValidStr;
			}
			else {
				$scope.lastValidStr = '';
			}
		};

		// Revert to last valid input
		$scope.revertInput = function() {
			$scope.checkRegexInput();

			// Leave input alone if not enforcing the regex maSk
			if ($scope.ctrl.forceregex !== 'false') {
				$scope.ctrl.value = $scope.lastValidStr;
                updateInvalid(false);
			}
		};
	}]
});

/**
 * fx-table
 * --------
 * callbacks: (none)
 * attrs: label, columns, rows
 * 
 * example data:
 * {
 *   columns: [
 *     "key name 1",
 *     "key name 2",
 *     "key name 3"
 *   ],
 *   rows: [
 *    { key1: "value1", key2: "value2", key3: "value3" },
 *    { key1: "value4", key2: "value5", key3: "value6" },
 *    { key1: "value7", key2: "value8", key3: "value9" }
 *   ]
 * }
 * 
 * For displaying a table from an array of strings (columns) and array of objects (rows)
 */
var fxTable = fxApp.component('fxTable', {
	templateUrl: 'directives/fxTable.html',
	transclude: true,
	bindings: {
		label: '@',
		columns: '<',
		rows: '<'
	},
	controller: ['$scope', 'fxWidgets', function($scope, fxWidgets) {
		$scope.ctrl = this;

		fxWidgets.enqueueEvent(function() {
			$('.dataTable').DataTable({
				"paging": true,
				"lengthChange": false,
				"searching": false,
				"ordering": true,
				"info": true,
				"autoWidth": false
			});
		});
	}]
});

/**
 * fx-raw-file
 * -----------
 * callbacks: onfile
 * expressions: onloaded
 * vars: label, accept, disabled, filestring
 * 
 * For entering a file via copy/paste or file upload
 */
var fxRawFile = fxApp.directive('fxRawFile', ['fxWidgets', function(fxWidgets) {
	return {
		templateUrl: 'directives/fxRawFile.html',
		restrict: 'E',
		scope: {
			label: '@',
			accept: '@',
			disabled: '@',
			filestring: '=',
			onfile: '=',
			onloaded: '&'
		},
		link: function(scope, element, attrs) {
			// hook into the file input change event
			function fileSelected(event) {
                var file = event.target.files[0];
                scope.onfile(file).then(function(value) {
                    scope.filestring = value;
                });
			}

			scope.clearSelection = function() {
				if (!scope.disabled) {
                    try {
                        scope.onfile(null);
                    } finally {
                        scope.filestring = '';
                    }
				}
			};

			element.find('input').bind('change', fileSelected);
		},
		controller: ['$scope', function($scope) {
			fxWidgets.enqueueEvent(function() {
				$scope.onloaded();
			});
		}]
    };
}]);

/**
 * fx-checkbox
 * -----------
 * callbacks: (none)
 * attrs: description, disabled, value
 * 
 * For setting/resetting a boolean
 */
var fxCheckbox = fxApp.component('fxCheckbox', {
	templateUrl: 'directives/fxCheckbox.html',
	bindings: {
		description: '@',
		disabled: '@',
		value: '='
	}
});

/**
 * fx-counter
 * ----------
 * callbacks: (none)
 * attrs: description, iconclass, color, count, total
 * 
 * For displaying a count progressing toward a total
 */
var fxCounter = fxApp.component('fxCounter', {
       templateUrl: 'directives/fxCounter.html',
       bindings: {
               description: '@',
               iconclass: '@',
               color: '@',
               count: '<',
               total: '<'
       },
       controller: ['$scope', function($scope) {
               $scope.bindings = this;

               $scope.progressWidth = function() {
                       return 100 * ($scope.bindings.count / $scope.bindings.total) + '%';
               };
       }]
});

/**
 * fx-port
 * -----------
 * callbacks: checkInput
 * attrs: description, disabled, config, relatedPorts, portType, value
 * config: min, max, monitoredPorts, portsLoaded
 *
 * For server ports: monitored ports must be polled asynchronously and passed in as relatedPorts
 *
 * For setting a port
 */
var fxPort = fxApp.component('fxPort', {
    templateUrl: 'directives/fxPort.html',
    bindings: {
        description: '@',
        disabled: '@',
        config: '<',
        relatedPorts: '<',
        portType: '<',
        value: '=',
        formInvalid: '=',
    },
    controller: ['$scope', function($scope) {
        var ctrl = this;

        // Related ports is optional
        if (ctrl.relatedPorts === undefined) {
            ctrl.relatedPorts = [];
        }

        // Using an already monitored port
        function usingMonitored() {
            return ctrl.config.monitoredPorts.indexOf(ctrl.value) >= 0;
        }

        // Using the same port as a different type
        function usingDuplicate() {
            var duplicateIndex = ctrl.relatedPorts.findIndex(function (config) {
                return ctrl.value === config.port && ctrl.portType !== config.type;
            });
            return duplicateIndex >= 0;
        }

        function getPortNames() {
            return ctrl.relatedPorts.map(function (config, index) {
                return '$ctrl.relatedPorts[' + index + '].port';
            });
        }

        var test = getPortNames();

        $scope.$watchGroup(getPortNames(), function() {
            $scope.checkInput();
        });

        $scope.checkInput = function() {
            $scope.invalid = usingMonitored() || usingDuplicate();
            ctrl.formInvalid = $scope.invalid;
        };
    }]
});

/**
 * fx-resize-listener
 * ------------------
 * callbacks: whenresize
 * 
 * Provides a way to register a callback for resizes that happen to individual
 * elements instead of just the entire window
 */
var fxResizeListener = fxApp.directive('fxResizeListener', ['$document', function($document) {
    // Create a generic element that can callback on resize events
    // with the same size and position, and append it as a child to
    // the element this directive is being applied to
    function attachResizeListener(elem, callback) {
        var listener = $document[0].createElement('object');
        listener.type = 'text/html';
        listener.data = 'about:blank';

        // Style the listener element to match the parent element's size and position
        // (must be applied to the style attribute and can't be a CSS class)
        var stylePosition = 'display: block; top: 0; left: 0;';
        var styleSize = 'height: 100%; width: 100%;';
        var styleBehavior = 'overflow: hidden; pointer-events: none; z-index: -1;';
        listener.setAttribute('style', stylePosition + styleSize + styleBehavior);

        // Hook into the resize event
        listener.onload = function(e) {
            this.contentDocument.defaultView.addEventListener('resize', callback);
        };

        // Attach the listener element to the provided element
        elem.appendChild(listener);
    }

    return {
        restrict: 'A',
        scope: {
            whenresize: '='
        },
        link: function(scope, element, attrs) {
            // Get the DOM reference from the jqLite wrapper object
            var DOMElemRef = element[0];

            // Handle the initial element size
            scope.whenresize(DOMElemRef);

            attachResizeListener(DOMElemRef, function(event) {
                // Handle resize events
                scope.whenresize(DOMElemRef);
            });
        }
    };
}]);

/**
 * fx-vue-wrapper
 * --------------
 * callbacks: (none)
 * attrs: shared
 *
 * Provides a wrapper for using a Vue component in an AngularJS app
 *
 * Note: You MUST always write the "ng-non-bindable" div that wraps the Vue
 * component(s) being transcluded. It cannot possibly be written in the the
 * template for this directive, nor can it be applied after-the-fact via DOM
 * manipulation in this directive's link function. There needs to be an explicit
 * boundary between AngularJS and Vue.
 *
 * Example:
 * <fx-vue-wrapper shared="someData">
 *     <div ng-non-bindable>
 *         <my-vue-component
 *             :some-prop="shared.something"
 *             :some-other-prop="shared.somethingElse">
 *         </my-vue-component>
 *     </div>
 * </fx-vue-wrapper>
 */
var fxVueWrapper = fxApp.directive('fxVueWrapper',
    ['fxAppModalService', function(fxAppModalService) {
    return {
        restrict: 'E',
        template: '<div ng-transclude></div>',
        transclude: true,
        scope: {
            shared: '=',
        },
        link: function(scope, elem) {
            new Vue({
                el: elem[0].querySelector('[ng-non-bindable]'),
                data: function() {
                    return {
                        shared: scope.shared,
                    };
                },
                updated: function() {
                    scope.$apply();
                },
                created: function () {
                    this.$bus.$on('showAlert', function (header, text) {
                        fxAppModalService.showModal(header, text);
                    });
                },
            });
        },
    };
}]);
