cmake_minimum_required(VERSION 3.12.0)
set(CMAKE_DISABLE_SOURCE_CHANGES ON)
set(CMAKE_DISABLE_IN_SOURCE_BUILD ON)
project(rag_demo CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(nlohmann_json 3.2.0 REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(spdlog 1.3.1 REQUIRED)
find_package(derecho CONFIG REQUIRED)
find_package(cascade CONFIG REQUIRED)

# Find Faiss package
find_package(Faiss REQUIRED)
# Find CUDA Toolkit if using Faiss with GPU support
find_package(CUDAToolkit REQUIRED)


include(GNUInstallDirs)
if (NOT DEFINED CMAKE_INSTALL_BINDIR)
    set(CMAKE_INSTALL_BINDIR bin)
endif()

if (NOT DEFINED CMAKE_INSTALL_LIBDIR)
    set(CMAKE_INSTALL_LIBDIR lib)
endif()

set(python_udl_VERSION 1.0)

find_package(Python3 3.10.0 QUIET COMPONENTS Interpreter Development Development.Module Development.Embed NumPy)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/config.h.in ${CMAKE_CURRENT_BINARY_DIR}/config.h)
add_library(python_udl SHARED python_udl.cpp)
target_include_directories(python_udl PRIVATE
    $<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
)
target_link_libraries(python_udl cascade Python3::Python Python3::NumPy)


add_library(clusters_search_udl SHARED clusters_search_udl.cpp)
target_include_directories(clusters_search_udl PRIVATE
    ${FAISS_INCLUDE_DIRS}
    $<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<BUILD_INTERFACE:${CMAKE_BINARY_DIR}>
)
target_link_libraries(clusters_search_udl PRIVATE derecho::cascade faiss CUDA::cudart)

add_custom_command(TARGET clusters_search_udl POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/cfg
        ${CMAKE_CURRENT_BINARY_DIR}/cfg
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/setup
        ${CMAKE_CURRENT_BINARY_DIR}/setup
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/python_udls
        ${CMAKE_CURRENT_BINARY_DIR}/python_udls
    COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/setup.py
        ${CMAKE_CURRENT_BINARY_DIR}/
    COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/client_query.py
        ${CMAKE_CURRENT_BINARY_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/layout.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n0/layout.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/layout.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n1/layout.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/layout.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n2/layout.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/layout.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n3/layout.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/layout.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/layout.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/layout.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/layout.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/layout.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/layout.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/dfgs.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n0/dfgs.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/dfgs.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n1/dfgs.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/dfgs.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n2/dfgs.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/dfgs.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n3/dfgs.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/dfgs.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/dfgs.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/dfgs.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/dfgs.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/dfgs.json.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/dfgs.json
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/udl_dlls.cfg.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n0/udl_dlls.cfg
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/udl_dlls.cfg.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n1/udl_dlls.cfg
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/udl_dlls.cfg.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n2/udl_dlls.cfg
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/udl_dlls.cfg.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n3/udl_dlls.cfg
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/udl_dlls.cfg.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/udl_dlls.cfg
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/udl_dlls.cfg.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/udl_dlls.cfg
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/udl_dlls.cfg.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/udl_dlls.cfg
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/setup
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/setup
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/setup
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/setup
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/setup
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/setup
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/setup.py
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/setup.py
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/setup.py
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/setup.py
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/setup.py
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/setup.py
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/client_query.py
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/client_query.py
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/client_query.py
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/client_query.py
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/client_query.py
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/client_query.py
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/python_udls
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n0/python_udls
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/python_udls
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n1/python_udls
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/python_udls
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n2/python_udls
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/python_udls
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n3/python_udls
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/python_udls
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/python_udls
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/python_udls
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/python_udls
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/python_udls
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/python_udls
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/run.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n0/run.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/run.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n1/run.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/run.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n2/run.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/run.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n3/run.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/run.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/run.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/run.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/run.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/run.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/run.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/clear_log.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n0/clear_log.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/clear_log.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n1/clear_log.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/clear_log.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n2/clear_log.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/clear_log.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n3/clear_log.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/clear_log.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n4/clear_log.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/clear_log.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n5/clear_log.sh 
    COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/cfg/clear_log.sh.tmp
        ${CMAKE_CURRENT_BINARY_DIR}/cfg/n6/clear_log.sh 
    COMMAND chmod 755 ${CMAKE_CURRENT_BINARY_DIR}/cfg/run.sh.tmp
    COMMAND chmod 755 ${CMAKE_CURRENT_BINARY_DIR}/cfg/clear_log.sh.tmp
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/cfg/run.sh.tmp
            ${CMAKE_CURRENT_SOURCE_DIR}/cfg/clear_log.sh.tmp
            ${CMAKE_CURRENT_SOURCE_DIR}/cfg/layout.json.tmp
            ${CMAKE_CURRENT_SOURCE_DIR}/cfg/dfgs.json.tmp
            ${CMAKE_CURRENT_SOURCE_DIR}/cfg/udl_dlls.cfg.tmp
            ${CMAKE_CURRENT_SOURCE_DIR}/setup.py
            ${CMAKE_CURRENT_SOURCE_DIR}/python_udls 
            ${CMAKE_CURRENT_SOURCE_DIR}/client_query.py
    COMMENT "prepare cluster search configuration"
)



# make install
install(TARGETS python_udl EXPORT cascade_python_udlTargets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/cascade_python_udlConfigVersion.cmake"
    VERSION ${python_udl_VERSION}
    COMPATIBILITY AnyNewerVersion
)

export (EXPORT cascade_python_udlTargets
    FILE "${CMAKE_CURRENT_BINARY_DIR}/cascade_python_udlTargets.cmake"
)

set(ConfigPackageLocation ${CMAKE_INSTALL_LIBDIR}/cmake/cascade_python_udl)

configure_package_config_file(cascade_python_udlConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/cascade_python_udlConfig.cmake"
    INSTALL_DESTINATION ${ConfigPackageLocation}
    PATH_VARS CMAKE_INSTALL_LIBDIR ConfigPackageLocation
)

install(EXPORT cascade_python_udlTargets
    FILE cascade_python_udlTargets.cmake
    NAMESPACE derecho::
    DESTINATION ${ConfigPackageLocation}
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/cascade_python_udlConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/cascade_python_udlConfigVersion.cmake"
    DESTINATION ${ConfigPackageLocation}
)

set(INSTALLED_PYTHON_UDL_LIB_FILE "${CMAKE_INSTALL_LIBDIR}/$<TARGET_FILE_NAME:python_udl>")

