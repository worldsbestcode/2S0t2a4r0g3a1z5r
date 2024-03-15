# Create install rules for protected javascript files
# This is only used by the angular projects
function(
    rkweb_jsprotected
    WEB_PROJECT
)
    # Working directories
    set(PROJ_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${WEB_PROJECT})

    # Find all protected files for project
    file(
        GLOB
        PROJ_DEPS
        ${PROJ_DIR}/protected_static/*
    )
    list(FILTER PROJ_DEPS INCLUDE REGEX "^.*\.js$")

    # null build that tracks dependencies
    set(TIMESTAMP_FILE ${CMAKE_CURRENT_BINARY_DIR}/.${WEB_PROJECT}.jsprotected.timestamp)
    add_custom_command(
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE}
        OUTPUT
            ${TIMESTAMP_FILE}
        DEPENDS
            ${SHARED_DEPS}
        COMMENT
            "Updating ${WEB_PROJECT} protected files"
    )
    set_source_files_properties(
        ${TIMESTAMP_FILE}
        PROPERTIES
            GENERATED 1
    )

    install(
        DIRECTORY ${PROJ_DIR}/protected_static/
        DESTINATION /var/www/${WEB_PROJECT}/protected
        COMPONENT fx-web-protected
        FILES_MATCHING PATTERN "*"
    )

    # Run this build when any of the project's static web files change
    add_custom_target(
        ${WEB_PROJECT}-protected
        ALL
        DEPENDS
            ${TIMESTAMP_FILE}
    )
endfunction()
