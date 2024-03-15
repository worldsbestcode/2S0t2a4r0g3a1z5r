# Install shared dependencies
function(
    rkweb_jsshared
)
    # shared working directory
    set(SHARED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/shared/js)

    # npm install
    set(TIMESTAMP_FILE ${CMAKE_CURRENT_BINARY_DIR}/.shared.js.timestamp)
    add_custom_command(
        COMMAND
            npm install
        COMMAND
            ${CMAKE_COMMAND} -E touch ${TIMESTAMP_FILE}
        OUTPUT
            ${TIMESTAMP_FILE}
        WORKING_DIRECTORY
            ${SHARED_DIR}
        DEPENDS
            ${SHARED_DIR}/package.json
            ${SHARED_DIR}/package-lock.json
        COMMENT
            "Installing shared dependencies"
    )

    # Reinstall when shared's files change
    add_custom_target(
        shared-web-js
        ALL
        DEPENDS
            ${TIMESTAMP_FILE}
            ${SERIAL_WEB_DEPS}
    )
    list(APPEND SERIAL_WEB_DEPS shared-web-js)
endfunction()

# Build front-end for JavaScript project
function(
    rkweb_jsbuild
    WEB_PROJECT
)
    # Working directories
    set(SHARED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/shared/js)
    set(PROJ_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${WEB_PROJECT}/js)

    # Find all files in proj/js/ as dependencies
    file(
        GLOB_RECURSE
        PROJ_DEPS
        ${PROJ_DIR}/*
    )
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*\.swp")
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*/dist/.*")
    list(FILTER PROJ_DEPS EXCLUDE REGEX ".*/node_modules/.*")

    # Find all files in shared/js/ as dependencies
    file(
        GLOB_RECURSE
        PROJ_SHARED_DEPS
        ${SHARED_DIR}/*
    )
    list(FILTER PROJ_SHARED_DEPS EXCLUDE REGEX ".*\.swp")

    # npm install and build
    set(TIMESTAMP_FILE ${CMAKE_CURRENT_BINARY_DIR}/.${WEB_PROJECT}.js.timestamp)
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
            ${PROJ_SHARED_DEPS}
        COMMENT
            "Building ${WEB_PROJECT} web front-end"
    )

    # Install rules
    install(
        DIRECTORY ${PROJ_DIR}/dist/
        DESTINATION /var/www/${WEB_PROJECT}/js
        COMPONENT rk-web-nginx
        FILES_MATCHING
            PATTERN "*"
            PATTERN "*.map" EXCLUDE
    )

    # Run this build when any of the project's js web files change
    add_custom_target(
        ${WEB_PROJECT}-web-js
        ALL
        DEPENDS
            shared-web-js
            ${TIMESTAMP_FILE}
            ${SERIAL_WEB_DEPS}
    )
    list(APPEND SERIAL_WEB_DEPS ${WEB_PROJECT}-web-js)
endfunction()
