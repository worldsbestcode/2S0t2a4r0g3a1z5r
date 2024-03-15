/**
 * Provides the data and callbacks for Angular Bootstrap Nav Tree
 *
 * @returns {object}    helper functions injected into view services
 */

var fxAppTreeService = fxApp.factory('fxAppTreeService',
	['$http', '$q', 'fxAppService',
	function($http, $q, fxAppService) {

	// Tree data and callbacks
	var treeData = [];
	var treeControl = {};

	function treeSelectEvent(){
	}

	function treeOnChanged(){
	}

	function treeWhenReady(){
	}

	// Tree pagination
	var updateTree = function(){};
	var paginationData = {
		filterCount: 0,
		pageCount: 0,
		itemsPerPage: 50,
		currentPage: 1
	};

	function totalPages() {
		return Math.ceil(paginationData.filterCount / paginationData.itemsPerPage);
	}

	function resetPage() {
		paginationData.currentPage = 1;
	}

	function canNext() {
		return paginationData.currentPage < totalPages();
	}

	function canPrev() {
		return paginationData.currentPage > 1;
	}

	function next() {
		fxAppTreeService.paginationData.currentPage += 1;
		updateTree();
	}

	function prev() {
		fxAppTreeService.paginationData.currentPage -= 1;
		updateTree();
	}

    /**
     * Get the page index
     * @returns {number}  The page index
     */
    function index() {
        return paginationData.currentPage - 1;
    }

    /**
     * Get the maximum page size
     * @returns {number}  The items per page
     */
    function pageSize() {
        return paginationData.itemsPerPage;
    }

	return {
		treeData: treeData,
		treeControl: treeControl,
		treeSelectEvent: treeSelectEvent,
		treeOnChanged: treeOnChanged,
		treeWhenReady: treeWhenReady,
		paginationData: paginationData,
		updateTree: updateTree,
		totalPages: totalPages,
		resetPage: resetPage,
		canNext: canNext,
		canPrev: canPrev,
		next: next,
        prev: prev,
        pageSize: pageSize,
        index: index
	};
}]);
