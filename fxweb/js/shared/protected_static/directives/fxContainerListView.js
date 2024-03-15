/**
 * An accordion based container list view
 * scope:
 *     groups: {Array} An array of groups to display in the list view
 *     groupColumns: {Array} A list of columns for the group
 *     childColumns: {Array} A list of child columns (if any)
 */
fxApp.directive('fxContainerListView', ['fxListContentService', function fxContainerListView(fxListContentService) {
        return {
        templateUrl: 'directives/fxContainerListView.html',
        restrict: 'E',
        scope: {
            currentSelection: '=',
            groups: '=',
            groupHeaderMapping: '=',
            childHeaderMapping: '=',
            groupTemplateUrl: '@?',
            childTemplateUrl: '@?',
            listRowTemplateUrl: '@?'
        },
        controller: ['$scope', function fxContainerListViewCtrl($scope) {
            $scope.ctrl = this;
            $scope.currentSelection.objectType = null;
            $scope.currentSelection.objectID = null;

            $scope.ctrl.childHeaderColumns = Object.keys($scope.childHeaderMapping);
            $scope.ctrl.groupHeaderColumns = Object.keys($scope.groupHeaderMapping);

            // Set group, child and listRow templates
            fxListContentService.setGroupTemplate($scope.groupTemplateUrl);
            fxListContentService.setChildTemplate($scope.childTemplateUrl);
            fxListContentService.setListRowTemplate($scope.listRowTemplateUrl);

            $scope.ctrl.childDisplayColumns = $scope.ctrl.childHeaderColumns.map(function (column) {
                return $scope.childHeaderMapping[column];
            });

            $scope.ctrl.groupDisplayColumns = $scope.ctrl.groupHeaderColumns.map(function (column) {
                return $scope.groupHeaderMapping[column];
            });

            $scope.ctrl.updateSelection = function (rowObject, isOpen) {
                var current = $scope.currentSelection;
                if (isOpen) {
                    current.objectID = rowObject.objectID;
                    current.objectType = rowObject.objectType;
                } else if (current.objectType == rowObject.objectType && current.objectID == rowObject.objectID) {
                    current.objectID = null;
                    current.objectType = null;
                }
            };

            $scope.ctrl.allExpanded = function() {
                return $scope.groups.reduce(function(result, group) {
                    return result && group.isOpen;
                }, true);
            };

            $scope.ctrl.expandAll = function() {
                $scope.groups.map(function(group) {
                    group.isOpen = true;
                });
            };

            $scope.ctrl.collapseAll = function() {
                $scope.groups.map(function(group) {
                    group.isOpen = false;
                });
            };
        }],
    }
}]);

/**
 * A component for list view rows
 */
fxApp.directive('fxListRow', ['fxListContentService', function (fxListContentService) {
    return {
        templateUrl: function(elements, attrs) {
            return fxListContentService.getTemplate(attrs.contentType);
        },
        scope: {
            rowColumns: '<',
            rowObject: '<',
            isOpen: '=?',
            updateSelection: '&?'
        },
        link: function (scope, element, attrs, listViewCtrl) {
            scope.$watch('isOpen', function (isOpen) {
                if (scope.updateSelection && scope.rowObject) {
                    scope.updateSelection()(scope.rowObject, isOpen);
                }

            });

            // Calculate the width of each column
            scope.calcWidth = function() {
                var width = 100 / scope.rowColumns.length;
                return "calc(" + width + "%)";
            };
        }
    };
}]);


/**
 * Controls the template urls of the list content service
 */
fxApp.factory('fxListContentService', function () {
    var defaultListContentTemplateUrl = 'directives/fxListContent.html';
    var defaultListRowTemplateUrl = 'directives/fxListRow.html';

    var defaultTemplates = {
        group: defaultListContentTemplateUrl,
        child: defaultListContentTemplateUrl,
        listRow: defaultListRowTemplateUrl
    }
    var templates = {
    };

    /**
     * Get a specific template type
     * @param {string}  contentType  The template type key
     * @return {string}  The template url or the default if not found
     */
    function getTemplate(contentType) {
        return templates[contentType] || defaultTemplates[contentType];
    }

    /**
     * Set a specific template type
     * @param {string}  contentType  The template type key
     * @param {string}  template  The template url
     * @return {function}  A closure for setting a specific type
     */
    function setTemplate(contentType) {
        return function (template) {
            templates[contentType] = template;
        };
    }

    return {
        setGroupTemplate: setTemplate('group'),
        setChildTemplate: setTemplate('child'),
        setListRowTemplate: setTemplate('listRow'),
        getTemplate: getTemplate,
    };
});

/**
 * A component for list view content
 */
fxApp.directive('fxListContent', ['fxListContentService', function(fxListContentService) {
    return {
        templateUrl: function(element, attrs) {
            return fxListContentService.getTemplate(attrs.contentType);
        },
        scope: {
            contentObject: '=',
            content: '='
        }
    };
}]);

fxApp.component('fxListContentRows', {
    templateUrl: 'directives/fxListContentRows.html',
    bindings: {
        content: '='
    }
});
