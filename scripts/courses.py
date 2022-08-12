#!/usr/local/bin/python3

import os
from pathlib import Path

import yaml

from config import (CURRENT_COURSE_ROOT, CURRENT_COURSE_SYMLINK,
                    CURRENT_COURSE_WATCH_FILE, CURRENT_SEMESTER_SYMLINK, ROOT)
from lectures import Lectures
from utils import recursive_iterdir


class Course():
    def __init__(self, path:Path):
        self.path = path
        self.name = path.stem

        self.info = yaml.safe_load((path / 'info.yaml').open())
        self._lectures = None

    @property
    def semester(self):
        return self.path.parent.stem

    @property
    def lectures(self):
        if not self._lectures:
            self._lectures = Lectures(self)
        return self._lectures

    def __eq__(self, other):
        if other == None:
            return False
        return self.path == other.path

    @property
    def is_activated(self):
        'Is the course the current course?'
        return os.path.samefile(self.path, CURRENT_COURSE_SYMLINK)

    @property
    def relative_path(self):
        return self.path.relative_to(ROOT)

    @staticmethod
    def is_course(path: Path):
        return path.is_dir() and (path / 'info.yaml').exists()


class Courses():

    @staticmethod
    def read_current_course():
        'Read the current course from the symlink, and return a new `Course` object'
        return Course(CURRENT_COURSE_SYMLINK.resolve())

    @staticmethod
    def set_current_course(course: Course):
        'Set the current course symlink to the given course'
        CURRENT_COURSE_SYMLINK.unlink()
        CURRENT_COURSE_SYMLINK.symlink_to(course.path)
        CURRENT_COURSE_WATCH_FILE.write_text(
            '{}\n'.format(course.info['short']))

    @staticmethod
    def read_files(path: Path = CURRENT_SEMESTER_SYMLINK):
        """
        Read all courses in path

        :param path: path to read courses from
        """
        course_directories = [x for x in recursive_iterdir(
            path) if x.is_dir() and Course.is_course(x)]
        _courses = [Course(path) for path in course_directories]
        return sorted(_courses, key=lambda c: c.name)

    def _load_courses(self):
        self.all_courses = Courses.read_files(self.path)

    def __init__(self, path=CURRENT_SEMESTER_SYMLINK):
        self.path = path
        self._load_courses()

    def __iter__(self):
        yield from self.all_courses

    @property
    def current(self):
        for course in self:
            if course.is_activated:
                return course
        raise Exception('No current course')

    @current.setter
    def current(self, course):
        Courses.set_current_course(course)

    @property
    def all(self):
        return self.all_courses


courses = Courses()
