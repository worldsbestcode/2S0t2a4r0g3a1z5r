/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2018
 * @brief Controls tabs for the balanced groups and devices
 */
fxApp.component('guardianObjectTab', {
    templateUrl: 'components/sections/guardianObjectTab.html',
    controller: ['$scope', 'guardianService', function ($scope, guardianService) {
        $scope.activeTab = {
            ref: 0,
        };

        $scope.guardianService = guardianService;

        $scope.logsShown = function () {
            return !guardianService.isSelectionDefaultDevice();
        };

        $scope.commandReportShown = function () {
            return !guardianService.isSelectionDefault() && guardianService.isSelectionGroup();
        };

        $scope.auditLogsShown = function () {
            return !guardianService.isSelectionDefault();
        };

        $scope.majorKeysShown = function () {
            return !guardianService.isSelectionGroup();
        };

        $scope.securitySettingsShown = function () {
            return guardianService.getSelectedObject().objectType === 'CARDGROUP';
        };

        $scope.vueShared = {
            selectionState: guardianService.vueOnlySelectionState,
            activeTab: $scope.activeTab,
        };
    }]
});
