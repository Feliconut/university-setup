#!/usr/local/bin/python3

import choose_courses
import choose_lectures
import choose_lectures_view
from choose import rofi,Rofi
# register all services and options
services = [choose_courses, choose_lectures, choose_lectures_view]

# generate list of all options, pass to choose
indices = []
options = []
opt_service = []
for service in services:
    options += service.options
    indices += list(range(0,len(service.options)))
    opt_service += [service]*len(service.options)

returncode, index, selected = rofi('Select option', options, [ ])
# parse the result, send to service process

if returncode == Rofi.SELECTED:
    try:
        service = opt_service[index]
        service.process(
            returncode,
            indices[index],
            selected
        )

    except IndexError:
        pass