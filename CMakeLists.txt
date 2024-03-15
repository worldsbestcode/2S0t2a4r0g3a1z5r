project(RemoteKey-Web)

set(PYTHON_VERSION "3.8" CACHE STRING "Version of python for rkweb")
find_program(PYTHON "python${PYTHON_VERSION}")

set(WEB_BASEDIR ${CMAKE_CURRENT_SOURCE_DIR})

# Install rule for shared nginx configuration
install(
    DIRECTORY ${WEB_BASEDIR}/nginx/conf/
    DESTINATION /etc/nginx/fx
    COMPONENT rk-web-nginx
)

# Install rule for shared nginx web files
install(
    DIRECTORY ${WEB_BASEDIR}/nginx/www/
    DESTINATION /var/www/nginx
    COMPONENT rk-web-nginx
)

# Install rule for shared static web files
install(
    DIRECTORY ${WEB_BASEDIR}/shared/static
    DESTINATION /var/www/shared/
    COMPONENT rk-web-nginx
)

# Install rule for shared python web files
install(
    DIRECTORY ${WEB_BASEDIR}/shared/python
    DESTINATION /var/www/shared/
    COMPONENT rk-web
)

# rkweb overlay
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../fs/rkweb/
    DESTINATION /
    USE_SOURCE_PERMISSIONS
    COMPONENT rk-web
)

# We will use this to force web builds to build serially
# If they all run at the same time it can cause pypi/npm timeouts on jenkins
set(SERIAL_WEB_DEPS)

# Python web helper microservices
include(cmake/venvbuild.cmake)
include(cmake/wheelbuild.cmake)

# Token refresh thread
rkweb_venvbuild(token-refresh)
rkweb_wheelbuild(token-refresh)

# Remote desktop prune thread
rkweb_venvbuild(prune-rd)
rkweb_wheelbuild(prune-rd)

# rk_add_web_build(WEB_PROJECT)
include(cmake/rkweb.cmake)

# Shared node modules
rkweb_jsshared()

# Projects
rk_add_web_build(cuserv)
rk_add_web_build(dki)
rk_add_web_build(home)
rk_add_web_build(rd)
rk_add_web_build(applogs)
rk_add_web_build(gekms)
rk_add_web_build(gcse)
rk_add_web_build(admin)
rk_add_web_build(iam)
rk_add_web_build(luds)

# Legacy web applications
rkweb_nginx(byok)
rkweb_jsbuild(byok)
rkweb_staticfiles(byok)

rkweb_nginx(regauth)
rkweb_jsbuild(regauth)
rkweb_staticfiles(regauth)
rkweb_jsprotected(regauth)

rkweb_nginx(guardian)
rkweb_jsbuild(guardian)
rkweb_staticfiles(guardian)
rkweb_jsprotected(guardian)

add_subdirectory(fxweb)
