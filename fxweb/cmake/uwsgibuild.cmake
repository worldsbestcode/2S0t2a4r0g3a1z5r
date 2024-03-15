# Install rule for uwsgi ini file for fxweb project
function(
    fxweb_uwsgibuild
)
    include(../cmake/uwsgibuild.cmake)
    rkweb_uwsgibuild(byok)
    rkweb_uwsgibuild(guardian)
    rkweb_uwsgibuild(kmes)
    rkweb_uwsgibuild(regauth)
endfunction()
