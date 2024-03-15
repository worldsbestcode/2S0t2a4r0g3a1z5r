# Build virtual environment for mounting into docker
function(
    rkweb_venvbuild
    WEB_PROJECT
)
    # Working directories
    set(PROJ_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${WEB_PROJECT}/python)
    set(SHARED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/shared/python)
    set(BUILD_DIR ${CMAKE_CURRENT_BINARY_DIR}/${WEB_PROJECT})

    # Requirements file is only dependency
    set(REQUIREMENTS ${PROJ_DIR}/requirements.txt)
    set(SHARED_REQUIREMENTS ${SHARED_DIR}/requirements.txt)

    # Build venv
    set(TIMESTAMP_FILE ${CMAKE_CURRENT_BINARY_DIR}/.${WEB_PROJECT}.venv.timestamp)
    add_custom_command(
        COMMAND
            mkdir -p ${BUILD_DIR}
        COMMAND
            ${PYTHON} -m venv ${BUILD_DIR}/venv
        COMMAND
            ${BUILD_DIR}/venv/bin/pip install --timeout 120 --upgrade pip
        COMMAND
            ${BUILD_DIR}/venv/bin/pip install --timeout 120 -r ${REQUIREMENTS}
        COMMAND
            ${BUILD_DIR}/venv/bin/pip install --timeout 120 -r ${SHARED_REQUIREMENTS}
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE}
        OUTPUT
            ${TIMESTAMP_FILE}
        DEPENDS
            ${REQUIREMENTS}
        COMMENT
            "Building ${WEB_PROJECT} web python virtualenv"
    )
    set_source_files_properties(
        ${TIMESTAMP_FILE}
        PROPERTIES
            GENERATED 1
    )

    # Run this build when the requirements file changes
    add_custom_target(
        ${WEB_PROJECT}-web-venv
        ALL
        DEPENDS
            ${TIMESTAMP_FILE}
            ${SERIAL_WEB_DEPS}
    )
    list(APPEND SERIAL_WEB_DEPS ${WEB_PROJECT}-web-venv)
endfunction()
