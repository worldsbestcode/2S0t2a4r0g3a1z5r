fxApp.component('keyView', { templateUrl: 'components/sections/keyView/content.html' });
fxApp.component('keyViewKeyEdit', { templateUrl: 'components/sections/keyView/keyEdit.html' });

var keyViewKeyEditCtrl = fxApp.controller('keyViewKeyEditCtrl', ['$scope', '$http', 'fxWidgets', function($scope, $http, fxWidgets){
	$scope.selectedKey = false;

	$scope.typeToString = function(arr){
		var result = '';
		for(var obj in arr){
			result += arr[obj].name + ',';
		}
		return result.slice(0, result.length-1);
	}

	$scope.keyTypes = [{id: 1, name: 'keyType1'}, {id: 2, name: 'keyType2'}, {id: 3, name: 'keyType3'}];
	$scope.encryptingKeyTypes = [{id: 1, name: 'encryptingKeyType1'}, {id: 2, name: 'encryptingKeyType2'}, {id: 3, name: 'encryptingKeyType3'}];
	$scope.algorithmTypes = [{id: 1, name: 'algorithmType1'}, {id: 2, name: 'algorithmType2'}, {id: 3, name: 'algorithmType3'}];
	$scope.keyLengthTypes = [{id: 1, name: 'keyLengthType1'}, {id: 2, name: 'keyLengthType2'}, {id: 3, name: 'keyLengthType3'}];
	$scope.usageTypes = [{id: 1, name: 'usageType1'}, {id: 2, name: 'usageType2'}, {id: 3, name: 'usageType3'}];
	$scope.typeTypes = [{id: 1, name: 'typeType1'}, {id: 2, name: 'typeType2'}, {id: 3, name: 'typeType3'}];
	$scope.bindingMethodTypes = [{id: 1, name: 'bindingMethodType1'}, {id: 2, name: 'bindingMethodType2'}, {id: 3, name: 'bindingMethodType3'}];
	$scope.keyUsageTypes = [{id: 1, name: 'keyUsageType1'}, {id: 2, name: 'keyUsageType2'}, {id: 3, name: 'keyUsageType3'}];
	$scope.modeOfUseTypes = [{id: 1, name: 'modeOfUseType1'}, {id: 2, name: 'modeOfUseType2'}, {id: 3, name: 'modeOfUseType3'}];
	$scope.keyVersionNumberTypes = [{id: 1, name: 'keyVersionNumberType1'}, {id: 2, name: 'keyVersionNumberType2'}, {id: 3, name: 'keyVersionNumberType3'}];
	$scope.exportabilityTypes = [{id: 1, name: 'exportabilityType1'}, {id: 2, name: 'exportabilityType2'}, {id: 3, name: 'exportabilityType3'}];
	$scope.attributeTypes = [
		{ key: $scope.keyTypes[0], value: 'myValue1', system_attr: true, standard_attr: false },
		{ key: $scope.keyTypes[0], value: 'myValue2', system_attr: false, standard_attr: true },
		{ key: $scope.keyTypes[0], value: 'myValue3', system_attr: true, standard_attr: true },
		{ key: $scope.keyTypes[0], value: 'myValue4', system_attr: false, standard_attr: false }
	];
	$scope.optionalBlockTypes = [
		{ use: true, value: 'myValue1', tag: 'tag1', description: 'description1' },
		{ use: false, value: 'myValue2', tag: 'tag2', description: 'description2' },
		{ use: true, value: 'myValue3', tag: 'tag3', description: 'description3' },
		{ use: false, value: 'myValue4', tag: 'tag4', description: 'description4' }
	];

	$scope.keys = [{
		objectType: 'keyGroup',
		objectData: {
			name: 'myKeys',
			keys: [{
				name: 'testKey',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[0], $scope.attributeTypes[2]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}, {
				name: 'testKey2',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[1], $scope.attributeTypes[3]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}, {
				name: 'testKey3',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[3], $scope.attributeTypes[0]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}]
		}
	}, {
		objectType: 'keyGroup',
		objectData: {
			name: 'myKeys2',
			keys: [{
				name: 'testKey',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[0], $scope.attributeTypes[2]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}, {
				name: 'testKey2',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[1], $scope.attributeTypes[3]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}, {
				name: 'testKey3',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[3], $scope.attributeTypes[0]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}]
		}
	}, {
		objectType: 'keyGroup',
		objectData: {
			name: 'myKeys3',
			keys: [{
				name: 'testKey',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[0], $scope.attributeTypes[2]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}, {
				name: 'testKey2',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[1], $scope.attributeTypes[3]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}, {
				name: 'testKey3',
				keyType: $scope.keyTypes[0],
				encryptingKey: $scope.encryptingKeyTypes[0],
				algorithm: $scope.algorithmTypes[0],
				keyLength: $scope.keyLengthTypes[0],
				modifier: 8,
				usage: $scope.usageTypes[0],
				type: $scope.typeTypes[0],
				parity: true,
				start_valid: randPastTime(),
				end_valid: randFutureTime(),
				owner: 'myOwner',
				address: 'myAddress',
				binding_method: $scope.bindingMethodTypes[0],
				key_usage: $scope.keyUsageTypes[0],
				mode_of_use: $scope.modeOfUseTypes[0],
				key_version_number: $scope.keyVersionNumberTypes[0],
				exportability: $scope.exportabilityTypes[0],
				attributes: [$scope.attributeTypes[3], $scope.attributeTypes[0]],
				optional_blocks: [$scope.optionalBlockTypes[0], $scope.optionalBlockTypes[1], $scope.optionalBlockTypes[2], $scope.optionalBlockTypes[3]]
			}]
		}
	}];

	// jsTree
	enqueueEvent(function(){
		// search box
		$("#key-tree-search").keyup(function(){
			var searchString = $(this).val();
			$('#key-tree').jstree('search', searchString);
		});

		// instance
		$('#key-tree').jstree({
			core: {
				data: formatToJSTree($scope.keys),
				themes: {
					name: 'proton',
					responsive: true
				}
			},
			search: {
				case_insensitive: true,
				show_only_matches : true
			},
			plugins: ['search', 'wholerow']
		});

		// set up events
		$('#key-tree').on('select_node.jstree', function(event, selected){
			// only if leaf node
			if (selected.node.children.length < 1){
				// assign selected key to $scope.selectedKey
				$scope.selectedKey = selected.node.original.original;
				$scope.$apply();
			}
			else {
				$scope.selectedKey = false;
				$scope.$apply();
			}
		});
	});
}]);

function randFutureTime(){
	var offset = Math.floor(Math.random() * 99999999999);
	return new Date(Date.now() + offset).toISOString();
}

function randPastTime(){
	var offset = Math.floor(Math.random() * 99999999999);
	return new Date(Date.now() - offset).toISOString();
}


// JSTree Stuff ////////////////////////////////////////////////////////////////
// need to generalize this to work with any depth of json
function formatToJSTree(input){
	var result = [];

	for(var obj in input){
		var parent = {
			text: input[obj].objectData.name,
			state: {
				opened: false,
				selected: false
			},
			children: []
		};

		for(var child in input[obj].objectData.keys){
			parent.children.push({
				text: input[obj].objectData.keys[child].name,
				original: input[obj].objectData.keys[child]
			});
		}
		result.push(parent);
	};

	return result;
}
////////////////////////////////////////////////////////////////////////////////

function enqueueEvent(callback){
	setTimeout(function(){
		callback();
	}, 0);
}
