# Functions for building rkweb
# rkweb_jsbuild(WEB_PROJECT)
include(cmake/jsbuild.cmake)

# rkweb_venvbuild(WEB_PROJECT)
include(cmake/venvbuild.cmake)

# rkweb_wheelbuild(WEB_PROJECT)
include(cmake/wheelbuild.cmake)

# rkweb_uwsgibuild(WEB_PROJECT)
include(cmake/uwsgibuild.cmake)

# rkweb_staticfiles(WEB_PROJECT)
include(cmake/staticfiles.cmake)

# rkweb_nginx(WEB_PROJECT)
include(cmake/nginx.cmake)

# rkweb_jsprotected(WEB_PROJECT)
include(cmake/jsprotected.cmake)

# Build all the components of an rkweb project
function(
    rk_add_web_build
    WEB_PROJECT
)
    rkweb_jsbuild(${WEB_PROJECT})
    rkweb_venvbuild(${WEB_PROJECT})
    rkweb_wheelbuild(${WEB_PROJECT})
    rkweb_uwsgibuild(${WEB_PROJECT})
    rkweb_staticfiles(${WEB_PROJECT})
    rkweb_nginx(${WEB_PROJECT})
endfunction()
