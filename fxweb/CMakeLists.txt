project(RemoteKey-FxWeb)

# Include subroutines
# fxweb_jsbuild()
include(cmake/jsbuild.cmake)

# fxweb_venvbuild()
include(cmake/venvbuild.cmake)

# fxweb_wheelbuild()
include(cmake/wheelbuild.cmake)

# fxweb_uwsgibuild()
include(cmake/uwsgibuild.cmake)

# fxweb_nginx()
include(cmake/nginx.cmake)

# Build components
fxweb_jsbuild()
fxweb_venvbuild()
fxweb_wheelbuild()
fxweb_uwsgibuild()
fxweb_nginx()

# Install run.py
install(
    FILES ${CMAKE_CURRENT_SOURCE_DIR}/python/run.py
    DESTINATION /var/www/fxweb/python/
    COMPONENT rk-web
)

# Install config files
file(
    GLOB
    CONFIG_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/python/config.cfg.*
)
install(
    FILES ${CONFIG_FILES}
    DESTINATION /etc/fx-web/
    COMPONENT rk-web
)
