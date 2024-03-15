/**
 * @author Matthew Seaworth <mseaworth@futurex.com>
 * @section LICENSE
 * This program is the property of Futurex, L.P.
 *
 * No disclosure, reproduction, or use of any part thereof may be made without
 * express written permission of Futurex L.P.
 *
 * Copyright by:  Futurex, LP. 2017
 * @brief Handles file and other io operations
 */
var fxIOService = fxApp.factory('fxIOService', ['$q', 'fxEncodeService', 'fxAppModalService',
    function($q, fxEncodeService, fxAppModalService) {
    var CHUNK_SIZE = 0x400000;  // The size of file chunks (4MiB)

    /**
     * Processes a complete blob/file in chunks
     * @param {function}  chunkCallback  Callback to process a single slice
     * @param {Blob}  blob  The blob/file to process
     * @returns {promise}  resolved after complete processing of file resolves with the bytes read
     */
    function chunkFile(chunkCallback, blob) {
        if (blob === null) {
            return $q.reject("No file given to chunk");
        }

        var deferred = $q.defer();
        var reader = new FileReader();
        var begin = 0;
        var end = CHUNK_SIZE;

        /**
         * @brief Read the next chunk
         * @param {integer}  offset  The amount to increment the beginning of the read by
         */
        function nextChunk(offset) {
            begin += offset;
            if (begin >= end) {
                end += CHUNK_SIZE;
                if (end > blob.size) {
                    end = blob.size;
                }
            }

            if (begin < blob.size) {
                var slice = blob.slice(begin, end);
                reader.readAsArrayBuffer(slice);
            } else if (begin >= blob.size) {
                // The reading is all done with async so we resolve here after completion
                deferred.resolve(begin);
            }
        }

        /**
         * Processes read result
         * @param {event} loadEvent  The event to process
         */
        reader.onload = function(loadEvent) {
            var target = loadEvent.target;
            if (target.error === null) {
                chunkCallback(target.result);
                nextChunk(target.result.byteLength);
            } else {
                deferred.reject(target.error);
            }
        };

        nextChunk(0);  // Begin reading chunks
        return deferred.promise;
    }

    /**
     * Handle file chunking
     * @param {string}  hashAlgorithm  The hashing algorithm
     * @param {Blob}  blob  The file/blob to process
     */
    function hashFile(hashAlgorithm, blob) {
        var options = {
            alg: hashAlgorithm === 'RIPEMD' ? 'RIPEMD-160' : hashAlgorithm,
            prov: 'cryptojs'
        };
        var hash = new KJUR.crypto.MessageDigest(options);

        /**
         * Update the hash using hex (the string version doesn't handle binary data)
         * @param {Array}  buffer  The data to update the hash with
         */
        function chunkAction(buffer) {
            hash.updateHex(fxEncodeService.arrayBufferToHex(buffer));
        }

        return chunkFile(chunkAction, blob).then(function() {
            return hash.digest();
        });
    }

    /**
     * Validate the file extension given a list of accepted types
     * @param {Array}  acceptedTypes  The allowed file type extensions
     * @param {string}  filename  The file name to check
     * @returns {promise}  deferred.promise  The result of the validation
     */
    function validateFileName(acceptedTypes, filename) {
        var extension = '.' + filename.split('.').pop();
        if (extension === filename) {
            return $q.reject("File name must contain characters in addition to the extension.");
        } else if (extension.substring(1) === filename) {
            return $q.reject("No file extension found.");
        }

        var deferred = $q.defer();
        var typesFound = acceptedTypes.filter(function(type) {
            return type === extension;
        });

        if (typesFound.length > 0) {
            deferred.resolve(true);
        } else {
            deferred.reject("These file types are valid: "+ acceptedTypes.join(','));
        }

        return deferred.promise;
    }

    /**
     * Read a file as a promise
     * @param {function}  readType  the read type to do
     * @param {File}  file  the file to read
     * @returns {promise}  deferred.promise  The result of the file read
     */
    function readFile(readType, file) {
        var deferred = $q.defer();
        var reader = new FileReader();

        reader.onload = function(load) {
            deferred.resolve(load.target.result);
        };

        reader.onerror = function(error) {
            deferred.reject(error);
        };

        readType(reader, file);
        return deferred.promise;
    }

    /**
     * Read and validate file as a promise
     * @param {function}  readType  the read type to do
     * @param {function}  validate  the validation function to execute
     * @param {File}  file  the file to read
     * @returns {promise}  deferred.promise  The result of the file read
     */
    function readAndValidate(validate, readType, file) {

        /**
         * Function for doing the file read after validation
         */
        function doRead() {
            return readFile(readType, file);
        }

        if (validate) {
            return validate(file).then(doRead, function(reason) {
                fxAppModalService.showModal('Error', reason);
            });
        }

        return doRead();
    }

    /**
     * Read in a signing request
     * @param {File}  file  the file to read in
     * @returns {promise}  A promise containing the hex encoded CSR on success
     */
    function readSigningRequest(inFile) {
        var requestFileTypes = ['.crt', '.cer', '.der', '.pem', '.csr'];

        /**
         * Checks the file extension
         * @param {File}  file  The file to name check
         * @returns {bool}  True if the name is in the accepted list false otherwise
         */
        function validateName(file) {
            return validateFileName(requestFileTypes, file.name);
        }

        /**
         * Callback for reading the CSR
         * @param {Filereader}  reader  The reader to use
         * @param {File}  file  The file to read
         */
        function readType(reader, file) {
            reader.readAsDataURL(file);
        }

        return readAndValidate(validateName, readType, inFile).then(function(data) {
            return fxEncodeService.dataUrlToHex(data);
        });
    }

    return {
        chunkFile: chunkFile,
        hashFile: hashFile,
        readAndValidate: readAndValidate,
        readFile: readFile,
        readSigningRequest: readSigningRequest,
        validateFileName: validateFileName
    };
}]);
