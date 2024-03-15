# Install rule for nginx configuration
function(
    rkweb_nginx
    WEB_PROJECT
)
    install(
        FILES ${CMAKE_CURRENT_SOURCE_DIR}/${WEB_PROJECT}/nginx/${WEB_PROJECT}.conf
        DESTINATION /etc/nginx/fx
        COMPONENT rk-web-nginx
    )
endfunction()
