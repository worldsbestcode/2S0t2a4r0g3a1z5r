fxApp.factory('fxSpinnerService', [function() {

    var spinners = {}; // store all spinners

    function isRegistered(name) {
        return spinners.hasOwnProperty(name);
    }

    function register(newSpinner) {
        if (newSpinner.hasOwnProperty('name') && !spinners.hasOwnProperty(newSpinner.name)) {
            // Only add a spinner if it isn't already in spinners
            spinners[newSpinner.name] = newSpinner;
        }
    }

    function show(name) {
        if(isRegistered(name)) {
            spinners[name].show();
        }
    }

    function remove(name) {
        if (isRegistered(name)) {
            spinners[name].remove();
            // de-register from spinners
            delete spinners[name];
        }
    }

    return {
        isRegistered: isRegistered,
        register: register,
        show: show,
        remove: remove,
    };

}]);
