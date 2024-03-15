# Build python bdist wheel for installing from debian package
function(
    rkweb_wheelbuild
    WEB_PROJECT
)
    # Working directories
    set(SHARED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/shared/python)
    set(PROJ_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${WEB_PROJECT}/python)
    set(BUILD_DIR ${CMAKE_CURRENT_BINARY_DIR}/${WEB_PROJECT}/python)

    # Find all files in proj/python/ as dependencies
    file(
        GLOB
        PROJ_DEPS
        ${PROJ_DIR}/*
    )
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*\.swp")
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*\.pyc")
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*__pycache__")

    # Find all files in shared/python/ as dependencies
    file(
        GLOB
        PROJ_SHARED_DEPS
        ${SHARED_DIR}/*
    )
    list(FILTER PROJ_SHARED_DEPS EXCLUDE REGEX ".*\.swp")
    list(FILTER PROJ_SHARED_DEPS EXCLUDE REGEX ".*\.pyc")
    list(FILTER PROJ_SHARED_DEPS EXCLUDE REGEX ".*__pycache__")

    # Setup working directory
    set(TIMESTAMP_FILE_DIR ${CMAKE_CURRENT_BINARY_DIR}/.${WEB_PROJECT}.py.timestamp.dir)
    add_custom_command(
        COMMAND
            mkdir -p ${BUILD_DIR}
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE_DIR}
        OUTPUT
            ${TIMESTAMP_FILE_DIR}
        COMMENT
            "Creating ${WEB_PROJECT} web python wheel build directory"
    )
    # Build wheel
    set(TIMESTAMP_FILE ${CMAKE_CURRENT_BINARY_DIR}/.${WEB_PROJECT}.py.timestamp)
    add_custom_command(
        COMMAND
            rm -rf ${BUILD_DIR}/${WEB_PROJECT}
        COMMAND
            cp -rv ${PROJ_DIR} ${BUILD_DIR}/${WEB_PROJECT}
        COMMAND
            cp -rv ${SHARED_DIR} ${BUILD_DIR}/shared
        COMMAND
            cp -v ${CMAKE_CURRENT_SOURCE_DIR}/setup.py ${BUILD_DIR}/
        COMMAND
            ${PYTHON} setup.py bdist_wheel --project=${WEB_PROJECT}
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE}
        OUTPUT
            ${TIMESTAMP_FILE}
        WORKING_DIRECTORY
            ${BUILD_DIR}
        DEPENDS
            ${TIMESTAMP_FILE_DIR}
            ${PROJ_DEPS}
            ${PROJ_SHARED_DEPS}
        COMMENT
            "Building ${WEB_PROJECT} web python wheel"
    )
    set_source_files_properties(
        ${TIMESTAMP_FILE}
        PROPERTIES
            GENERATED 1
    )

    # Add wheel to rk-web package
    install(
        DIRECTORY ${BUILD_DIR}/dist
        DESTINATION /var/www/${WEB_PROJECT}/python
        COMPONENT rk-web
        FILES_MATCHING PATTERN "*.whl"
    )

    # Run this build when any of the project's python files change
    add_custom_target(
        ${WEB_PROJECT}-web-wheel
        ALL
        DEPENDS
            ${TIMESTAMP_FILE}
            ${SERIAL_WEB_DEPS}
    )
    list(APPEND SERIAL_WEB_DEPS ${WEB_PROJECT}-web-wheel)
endfunction()
