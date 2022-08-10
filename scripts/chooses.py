#!/usr/local/bin/python3

import choose_courses
import choose_lectures
import choose_lectures_view
from choose import rofi, Rofi
# register all services and options
services = [choose_courses, choose_lectures, choose_lectures_view]

# generate list of all options, pass to choose
# (service, indice, opt)
data = []
for service in services:
    data += list(zip(
        [service]*len(service.options),
        list(range(len(service.options))),
        service.options))

returncode, index, selected = rofi('Select option', [option for _,_,option in data], [])
# parse the result, send to service process

if returncode == Rofi.SELECTED:
    try:
        service, serv_index, selected = data[index]
        service.process(
            returncode,
            serv_index,
            selected
        )

    except IndexError:
        pass
