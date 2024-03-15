/**
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017
 * @brief Filter functions and filter schema functions
 */
var filterService = fxApp.factory('filterService', [function() {

    /**
     * Create a filter entry
     * @param {string}  entryType  The type of entry
     * @param {bool}  canBeExact  If this entry can have exact/inexact matched
     * @param {Array}  options  A list of choices for a type
     * @param {Array}  objectTypes A list of associated object types that can query by this field
     * @param {Array}  baseObjectType The base object type that this field should query
     * @returns {object}  An object representing the filter entry
     */
    function filterEntry(entryType, canBeExact, options, objectTypes, baseObjectType) {
        if (options) {
            return {type: entryType, canBeExact: canBeExact, options: options, objectTypes: objectTypes, baseObjectType: baseObjectType};
        }

        return {type: entryType, canBeExact: canBeExact, objectType: objectTypes, baseObjectType: baseObjectType};
    }

    var fields = {
        entry: filterEntry,

        /**
         * Creates a filter entry for a set of choices
         * @param {Array}  options  A list of choices for a type
         * @param {Array}  objectTypes A list of associated object types that can query by this field
         * @param {String}  baseObjectType The base object type that this field should query
         * @returns {object}  An object representing the enumerated entry
         */
        setList: function (options, objectTypes, baseObjectType) {
            return filterEntry('Select', false, options, objectTypes, baseObjectType);
        },

        /**
         * Create date range lookup types
         * @param {Array}  objectTypes A list of associated object types that can query by this field
         * @param {String}  baseObjectType The base object type that this field should query
         * @returns {object}  An entry for date ranges
         */
        dateRange: function (objectTypes, baseObjectType) {
            return filterEntry('DateRange', false, [], objectTypes, baseObjectType);
        },

        /**
         * Create a filter entry for text that must be exact
         * @param {Array}  objectTypes A list of associated object types that can query by this field
         * @param {String}  baseObjectType The base object type that this field should query
         * @returns {object} An entry for regular text
         */
        exactText: function (objectTypes, baseObjectType) {
            return filterEntry('ExactText', true, [], objectTypes, baseObjectType);
        },

        /**
         * Create a filter entry for text
         * @param {Array}  objectTypes A list of associated object types that can query by this field
         * @param {String}  baseObjectType The base object type that this field should query
         * @returns {object} An entry for regular text
         */
        nonExactText: function (objectTypes, baseObjectType) {
            return filterEntry('Text', false, [], objectTypes, baseObjectType);
        },

        /**
         * Create a filter entry for text
         * @param {Array}  objectTypes A list of associated object types that can query by this field
         * @param {String}  baseObjectType The base object type that this field should query
         * @returns {object}  An entry for exact text
         */
        text: function (objectTypes, baseObjectType) {
            return filterEntry('Text', true, [], objectTypes, baseObjectType);
        }
    };

    /**
     * Filtering allowed for anonymous users
     * @return {object}  criteria  The filtering options for anonymous users
     */
    function anonymousCriteria() {
        var objectTypes = ['Approvable Object', 'Certificate Request', 'Signable Object'];
        var criteria = {};
        objectTypes.forEach(function (objectType) {
            criteria[objectType] = {
                'Uploader E-mail': fields.exactText(objectTypes, objectType)
            };
        });

        return criteria;
    }

    /**
     * @returns {object}  Approval Group schema
     */
    function approvalGroup() {
        var baseObjectType = 'Approval Group';
        return {'Name': fields.text([baseObjectType], baseObjectType)};
    }

    /**
     * Properties of approvable objects which are shared by CSRs and signable objects
     * @returns {object}  Approvable filter properties
     */
    function approvableObject() {
        var baseObjectType = 'Approvable Object';
        var objectTypes = ['Approvable Object', 'Certificate Request', 'Signable Object'];
        return {
            'Type': fields.setList(['X.509', 'Hash'], objectTypes, baseObjectType),
            'Status': fields.setList(['pending', 'signed', 'denied'], objectTypes, baseObjectType),
            'Name': fields.text(objectTypes, baseObjectType),
            'Unique ID': fields.text(objectTypes, baseObjectType),
            'Notes': fields.text(objectTypes, baseObjectType),
            'Uploader': fields.text(objectTypes, baseObjectType),
            'Uploaded': fields.dateRange(objectTypes, baseObjectType),
            'Uploader E-mail': fields.text(objectTypes, baseObjectType)
        };
    }

    /**
     * Creates an empty filter for audit logs
     * @param {bool}  useGroupConfig  True if we are using group configuration
     * @returns {object}  Audit log schema
     */
    function auditLog(useGroupConfig) {
        var baseObjectType = 'Log';
        var objectTypes = [baseObjectType];
        var logTypes = [
            'Generic',
            useGroupConfig ? 'Group Configuration' : 'Key Injection',
            'Key Entry',
            'Configuration',
            'Addition or Deletion',
            'Device',
            'Syslog',
            'Token personalization',
            'Approval'
        ];

        return {
            'Date': fields.dateRange(objectTypes, baseObjectType),
            'Summary': fields.text(objectTypes, baseObjectType),
            'Users': fields.text(objectTypes, baseObjectType),
            'Log Type': fields.setList(logTypes, objectTypes, baseObjectType),
            'Details': fields.text(objectTypes, baseObjectType)
        };
    }

    /**
     * Properties of certificate request object
     * @returns {object}  Filter properties of certificate request
     */
    function certificateRequest () {
        var baseObjectType = 'Certificate Request';
        var objectTypes = [baseObjectType];
        return {
            'Subject': fields.nonExactText(objectTypes, baseObjectType),
            'Extensions': fields.nonExactText(objectTypes, baseObjectType),
            'Expiration': fields.dateRange(objectTypes, baseObjectType),
            'Key Type': fields.text(objectTypes, baseObjectType)
        };
    }

    /**
     * Properties of signable object request
     * @returns {object}  Filter properties of signable object
     */
    function signableObject () {
        var baseObjectType = 'Signable Object';
        var objectTypes = [baseObjectType];
        return {
            'Padding Mode': fields.setList(['PKCS1', 'PSS', 'X931'], objectTypes, baseObjectType),
            'Salt Length': fields.text(objectTypes, baseObjectType)
        };
    }

    /**
     * Properties of a signing approver object request
     * @returns {object} Filter properties of a signing approver object
     */
    function signingApprover() {
        var baseObjectType = 'Signing Approvers';
        var objectTypes = [baseObjectType];
        return {
            'Approved': fields.setList(['Approved', 'Denied'], objectTypes, baseObjectType),
            'Date'    : fields.dateRange(objectTypes, baseObjectType),
        };
    }

    /**
     * Object field schema without inheritance
     * @param   {string}  objectType - The object type
     * @returns {object}  The object field schema of the given type
     */
    function objectFieldSchema(objectType) {
        var schemas = {
            APPROVAL_GROUP: approvalGroup,
            APPROVABLE_OBJ: approvableObject,
            CERT_REQ: certificateRequest,
            LOG: auditLog,
            SIGNABLE_OBJ: signableObject,
            SIGNING_APPROVERS: signingApprover
        };

        return schemas[objectType]();
    }


    /**
     * Creates a filter value clause
     * @param {string}  objectType - The object type
     * @param {string}  field - The clause property
     * @param {string}  value - The value to search for
     * @param {string}  condition - The match type (optional)
     * @param {bool}  exactMatch - If the match should be exact (optional)
     * @return {object}  The filter clause
     */
    function valueClause(objectType, field, value, condition, exactMatch) {
        return {
            clauseCondition: condition ? condition : 'AND',
            enabled: true,
            exactMatch: exactMatch === true,
            field: field,
            incomplete: false,
            maxValue: "",
            minValue: "",
            objectType: objectType,
            valueToMatch: value
        };
    }

    /**
     * Creates a filter value clause containing al necessary filter clause
     * components.
     *
     * This is used for non-range clauses.
     *
     * @param {string} objectType The object type
     * @param {string} field The clause property
     * @param {string} value The value to search for
     * @param {string} condition The match type. default=AND.
     * @param {string} match If the match should be exact. default=EXACT.
     *
     * @return {object} The filter clause
     */
    function createFullClause(objectType, field, value, condition, match) {
      return {
        operator: condition || 'AND',
        match: match || 'EXACT',
        objectType: objectType,
        field: field,
        maxValue: '',
        minValue: '',
        value: value
      };
    }

    /**
     * Any filter parameters that change the result data
     *
     * @param {string}  manager - The object manager type
     * @param {string}  type - The filter type (optional)
     * @param {object}  ids - The object id container (optional)
     * @param {Array}  flags - A list of filter flags (optional)
     * @param {string}  distinct - The column to restrict to distinct results
     *
     * @returns {object}  An object containing request data
     */
    function requestData(manager, type, ids, flags, distinct) {
        return {
            distinct: distinct ? distinct : '',
            manager: manager,
            type: type ? type : 'RESULTS',
            flags: flags ? flags : [],
            ids: ids ? ids : {}
        };
    }

    /**
     * Anything that manipulates the returned results without changing the returned data
     *
     * @param {number}  size - The chunking size
     * @param {number}  index - The chunk index (optional)
     * @param {string}  column - The sorting column (optional)
     * @param {boolean}  ascending - If the results should be in ascending order (optional)
     *
     * @returns {object} An object containing the ordering data
     */
    function orderingData(size, index, column, ascending) {
        return {
            column: column ? column : '',
            index: index ? index : 0,
            size: size,
            ascending: ascending === true
        };
    }

    /**
     * Create a new filter object
     * @param {object}  request - The request information
     * @param {object}  ordering - The ordering information container
     * @param {Array}  clauses - Filter clauses (optional)
     *
     * @returns {object}  A filter object
     */
    function makeFilter(request, ordering, clauses) {
        return {
            "method": "retrieve",
            "objectType": "Filter",
            "quantity": ordering.size,
            "request": {
                "manager": request.manager,
                "chunk": ordering.index,
                "chunkSize": ordering.size,
                "flags": request.flags,
                "filterType": request.type,
                "sortAscending": ordering.ascending,
                "sortColumn": ordering.column,
                "distinctOn": request.distinct,
                "objectIDs": request.ids,
                "clauses": clauses ? clauses : []
            }
        };
    }


    /**
     * Prepares a clause to be used in a filter query
     *
     * @param   {object}    an individual filter clause
     * @param   {object}    filterOptions - the filter clause options
     * @returns {promise}   resolved upon receiving the response
     */
    function prepareClause(clause) {
        // get field type
        var fieldOptions = clause.fieldOptions;

        // the base format of a filter clause
        var baseClause = {
            objectType: fieldOptions.baseObjectType,
            field: clause.field.toLowerCase(),
            operator: clause.clauseCondition,
            match: clause.exactMatch ? 'EXACT' : 'PARTIAL',
            value: clause.valueToMatch,
            minValue: '',
            maxValue: ''
        };

        // modify the clause based on field type
        var fieldType = fieldOptions.type;
        if (fieldType === 'DateRange') {
            baseClause.match = 'DATE_DELTA_RANGE';
            baseClause.value = '';
            baseClause.minValue = clause.minValue;
            baseClause.maxValue = clause.maxValue;
        } else if (fieldType === 'Select') {
            baseClause.match = 'EXACT';
            baseClause.value = clause.valueToMatch;
            baseClause.minValue = '';
            baseClause.maxValue = '';
        }

        return baseClause;
    }

    /**
     * Prepares a clause array
     * This function can be called in two ways
     * 1. no filterOptions - with options already embedded in the clauses
     * 2. filterOptions - this will apply to all clauses
     * @param {Array}  clauses - The list of clauses to prepare
     * @returns {Array}  A list of prepared clauses
     */
    function prepareClauses(clauses, filterOptions) {
        return clauses.filter(function (clause) {
            return clause.enabled;
        }).map(function (clause) {
            var toPrepare = clause;
            if (filterOptions) {
                var clonedClause = Object.assign({}, clause);
                var fieldOptions = getFieldOptions(clonedClause, filterOptions);
                clonedClause.fieldOptions = fieldOptions;

                toPrepare = clonedClause;
            }
            return prepareClause(toPrepare);
        });
    }

    /**
     * Get the options for the selected object type and field
     *
     * @param   {object} clause - a single clause from the dialog
     * @param   {object} options - the filter options passed into the filter
     * @returns {object} the options
     */
    function getFieldOptions(clause, options) {
        var objectType = clause.objectType;
        var field = clause.field;
        var fieldOptions = options.criteria[objectType][field];
        return fieldOptions;
    }

    return {
        anonymousCriteria: anonymousCriteria,
        createFullClause: createFullClause,
        filterEntry: filterEntry,
        filterField: fields,
        makeFilter: makeFilter,
        objectFieldSchema: objectFieldSchema,
        orderingData: orderingData,
        prepareClauses: prepareClauses,
        requestData: requestData,
        schema: {
            approvableObject: approvableObject,
            approvalGroup: approvalGroup,
            auditLog: auditLog,
            certificateRequest: certificateRequest,
            signableObject: signableObject,
            signingApprover: signingApprover
        },
        valueClause: valueClause
    };
}]);
