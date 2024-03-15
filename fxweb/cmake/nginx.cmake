# Install rule for nginx configuration
function(
    fxweb_nginx
)
    file(
        GLOB
        CONF_FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/nginx/*
    )

    install(
        FILES ${CONF_FILES}
        DESTINATION /etc/nginx/fx
        COMPONENT rk-web-nginx
    )
endfunction()
