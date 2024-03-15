/**
 * AdminLTE header
 */
fxApp.component('fxHeader', {
	templateUrl: 'components/sections/header.html'
});

/**
 * AdminLTE header with no sidebbar
 */
fxApp.component('fxHeaderNoSidebar', {
	templateUrl: 'components/sections/headerNoSidebar.html'
});

/**
 * AdminLTE footer
 */
fxApp.component('fxFooter', {
	templateUrl: 'components/sections/footer.html'
});

/**
 * Placeholder when nothing from the sidebar is selected
 */
fxApp.component('landingPlaceholder', {
	templateUrl: 'components/sections/placeholder.html'
});

/**
 * AdminLTE box
 */
fxApp.component('fxBox', {
	templateUrl: 'components/idioms/box.html',
	transclude: true
});

/**
 * AdminLTE box with an icon in the upper right corner
 */
fxApp.component('fxIconBox', {
	templateUrl: 'components/idioms/iconBox.html',
	transclude: true,
	bindings: {
		iconclass: '@'
	}
});

/**
 * Bootstrap column
 */
fxApp.component('fxColumn', {
	templateUrl: 'components/idioms/column.html',
	transclude: true,
	bindings: {
		width: '@',
		innerstyle: '@'
	}
});

/**
 * Bootstrap row
 */
fxApp.component('fxRow', {
	templateUrl: 'components/idioms/row.html',
	transclude: true
});

/**
 * AdminLTE box with loading state icon
 */
fxApp.component('fxOverlayBox', {
	templateUrl: 'components/idioms/overlayBox.html',
	transclude: true,
	bindings: {
		overlayState: '='
	}
});
