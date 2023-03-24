set(MAN_PAGES
  nihtest.1
  nihtest-case.5
  nihtest.conf.5
  )

foreach(MAN_PAGE ${MAN_PAGES})
  string(REGEX REPLACE "[1-9]$" "${DOCUMENTATION_FORMAT}" SOURCE_FILE ${MAN_PAGE})
  if(NIHTEST_DO_INSTALL)
    if (DOCUMENTATION_FORMAT MATCHES "html")
      install(FILES ${PROJECT_BINARY_DIR}/man/${MAN_PAGE} DESTINATION ${CMAKE_INSTALL_DOCDIR} RENAME ${SOURCE_FILE})
    else()
      string(REGEX REPLACE ".*(.)$" "man\\1" SUBDIR ${MAN_PAGE})
      install(FILES ${PROJECT_BINARY_DIR}/man/${MAN_PAGE} DESTINATION ${CMAKE_INSTALL_MANDIR}/${SUBDIR})
    endif()
  endif()
  # configure_file does not find out about updates to the sources, and it does not provide a target
  #configure_file(${SOURCE_FILE} ${MAN_PAGE} COPYONLY)
  add_custom_command(OUTPUT ${MAN_PAGE}
    DEPENDS ${SOURCE_FILE}
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${PROJECT_SOURCE_DIR}/man/${SOURCE_FILE} ${PROJECT_BINARY_DIR}/man/${MAN_PAGE}
    COMMENT "Preparing ${MAN_PAGE}"
    )

  string(REGEX REPLACE "[1-9]$" "html" HTML_FILE ${MAN_PAGE})
  string(REGEX REPLACE "[1-9]$" "man" MAN_FILE ${MAN_PAGE})
  string(REGEX REPLACE "[1-9]$" "mdoc" MDOC_FILE ${MAN_PAGE})

  # html re-generation
  add_custom_command(OUTPUT ${PROJECT_SOURCE_DIR}/man/${HTML_FILE}
    DEPENDS ${MDOC_FILE}
    COMMAND ${CMAKE_COMMAND} -DIN=${MDOC_FILE} -DOUT=${HTML_FILE} -DDIR=${PROJECT_SOURCE_DIR}/man -P ${PROJECT_SOURCE_DIR}/man/update-html.cmake
    )
  list(APPEND UPDATEHTML ${PROJECT_SOURCE_DIR}/man/${HTML_FILE})

  # man re-generation
  add_custom_command(OUTPUT ${PROJECT_SOURCE_DIR}/man/${MAN_FILE}
    DEPENDS ${MDOC_FILE}
    COMMAND ${CMAKE_COMMAND} -DIN=${MDOC_FILE} -DOUT=${MAN_FILE} -DDIR=${PROJECT_SOURCE_DIR}/man -P ${PROJECT_SOURCE_DIR}/man/update-man.cmake
    )
  list(APPEND UPDATEMAN ${PROJECT_SOURCE_DIR}/man/${MAN_FILE})
endforeach()
add_custom_target(man ALL DEPENDS ${MAN_PAGES})
add_custom_target(update-man DEPENDS ${UPDATEMAN})
add_custom_target(update-html DEPENDS ${UPDATEHTML})
