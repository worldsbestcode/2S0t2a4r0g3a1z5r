# Build python bdist wheel for installing from debian package
function(
    fxweb_wheelbuild
)
    # Working directories
    set(PROJ_DIR ${CMAKE_CURRENT_SOURCE_DIR}/python)
    set(BUILD_DIR ${CMAKE_CURRENT_BINARY_DIR}/python)

    # Find all files in proj/python/ as dependencies
    file(
        GLOB
        PROJ_DEPS
        ${PROJ_DIR}/*
    )
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*\.swp")
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*\.pyc")
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*__pycache__")

    # Setup working directory
    set(TIMESTAMP_FILE_DIR ${CMAKE_CURRENT_BINARY_DIR}/.py.timestamp.dir)
    add_custom_command(
        COMMAND
            mkdir -p ${BUILD_DIR}
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE_DIR}
        OUTPUT
            ${TIMESTAMP_FILE_DIR}
        COMMENT
            "Creating fxweb python wheel build directory"
    )
    # Build wheel
    set(TIMESTAMP_FILE ${CMAKE_CURRENT_BINARY_DIR}/.py.timestamp)
    add_custom_command(
        COMMAND
            rm -rf ${BUILD_DIR}/*
        COMMAND
            cp -rv ${PROJ_DIR}/* ${BUILD_DIR}/
        COMMAND
            cp -v ${PROJ_DIR}/setup.py ${BUILD_DIR}/
        COMMAND
            ${PYTHON} setup.py bdist_wheel
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE}
        OUTPUT
            ${TIMESTAMP_FILE}
        WORKING_DIRECTORY
            ${BUILD_DIR}
        DEPENDS
            ${TIMESTAMP_FILE_DIR}
            ${PROJ_DEPS}
        COMMENT
            "Building fxweb python wheel"
    )
    set_source_files_properties(
        ${TIMESTAMP_FILE}
        PROPERTIES
            GENERATED 1
    )

    # Add wheel to rk-web package
    install(
        DIRECTORY ${BUILD_DIR}/dist
        DESTINATION /var/www/fxweb/python
        COMPONENT rk-web
        FILES_MATCHING PATTERN "*.whl"
    )

    # Run this build when any of the project's python files change
    add_custom_target(
        fxweb-wheel
        ALL
        DEPENDS
            ${TIMESTAMP_FILE}
    )
endfunction()
