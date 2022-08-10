#!/usr/bin/python3
from rofi import rofi

from courses import Courses

courses = Courses()
current = courses.current

try:
    current_index = courses.index(current)
    args = ['-a', current_index]
except ValueError:
    args = []


def process(code, index, selected):
    print((code, index, selected))
    if index >= 0:
        courses.current = courses[index]


if __name__ == '__main__':
    process(*rofi('Select course', [c.info['title'] for c in courses], [
    ] + args))
