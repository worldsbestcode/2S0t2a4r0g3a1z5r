# Install rule for uwsgi ini file for rkweb project
function(
    rkweb_uwsgibuild
    WEB_PROJECT
)
    # Decide if we want to use the generic one or a specialized one
    set(UWSGI_FILE ${CMAKE_CURRENT_SOURCE_DIR}/${WEB_PROJECT}/uwsgi.ini)
    if (NOT EXISTS ${UWSGI_FILE})
        set(UWSGI_FILE ${CMAKE_CURRENT_SOURCE_DIR}/uwsgi.ini)
    endif()

    install(
        FILES ${UWSGI_FILE}
        DESTINATION /etc/rk-web/vassals
        RENAME ${WEB_PROJECT}.ini
        COMPONENT rk-web
    )
endfunction()
