# Build front-end for FxWeb JavaScript
function(
    fxweb_jsbuild
)
    # Working directories
    set(PROJ_DIR ${CMAKE_CURRENT_SOURCE_DIR}/js)

    # Find all files in proj/js/ as dependencies
    file(
        GLOB
        PROJ_DEPS
        ${PROJ_DIR}/*
    )
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*\.swp")
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*/dist/.*")
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*/node_modules/.*")

    # npm install and build
    set(TIMESTAMP_FILE ${CMAKE_CURRENT_BINARY_DIR}/.js.timestamp)
    add_custom_command(
        COMMAND
            npm install
        COMMAND
            npm run build
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE}
        OUTPUT
            ${TIMESTAMP_FILE}
        WORKING_DIRECTORY
            ${PROJ_DIR}
        DEPENDS
            ${PROJ_DEPS}
        COMMENT
            "Building fxweb front-end"
    )
    set_source_files_properties(
        ${TIMESTAMP_FILE}
        PROPERTIES
            GENERATED 1
    )

    # Run this build when any of the project's js web files change
    add_custom_target(
        fxweb-js
        ALL
        DEPENDS
            ${TIMESTAMP_FILE}
    )

    # Install rules
    install(
        DIRECTORY ${PROJ_DIR}/shared/static/
        DESTINATION /var/www/fxweb/static
        COMPONENT rk-web-nginx
        FILES_MATCHING PATTERN "*"
    )
    install(
        DIRECTORY ${PROJ_DIR}/shared/protected_static/
        DESTINATION /var/www/fxweb/protected_static
        COMPONENT rk-web-nginx
        FILES_MATCHING PATTERN "*"
    )
endfunction()
