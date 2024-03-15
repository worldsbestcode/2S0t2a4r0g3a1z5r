# Create install rules for static files
function(
    rkweb_staticfiles
    WEB_PROJECT
)
    # Working directories
    set(PROJ_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${WEB_PROJECT}/static)

    # Find all files in proj/static/ as dependencies
    file(
        GLOB
        PROJ_DEPS
        ${PROJ_DIR}/*
    )
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*\.swp")

    # null build
    set(TIMESTAMP_FILE ${CMAKE_CURRENT_BINARY_DIR}/.${WEB_PROJECT}.static.timestamp)
    add_custom_command(
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE}
        OUTPUT
            ${TIMESTAMP_FILE}
        DEPENDS
            ${PROJ_DEPS}
        COMMENT
            "Updating ${WEB_PROJECT} static files"
    )
    set_source_files_properties(
        ${TIMESTAMP_FILE}
        PROPERTIES
            GENERATED 1
    )

    # Install rules
    install(
        DIRECTORY ${PROJ_DIR}/
        DESTINATION /var/www/${WEB_PROJECT}/static
        COMPONENT rk-web-nginx
        FILES_MATCHING PATTERN "*"
    )

    # Run this build when any of the project's static web files change
    add_custom_target(
        ${WEB_PROJECT}-web-static
        ALL
        DEPENDS
            ${TIMESTAMP_FILE}
    )
endfunction()
