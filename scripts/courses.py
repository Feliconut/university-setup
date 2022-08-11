#!/usr/local/bin/python3

from pathlib import Path

import yaml

from config import (CURRENT_COURSE_ROOT, CURRENT_COURSE_SYMLINK,
                    CURRENT_COURSE_WATCH_FILE, CURRENT_SEMESTER_SYMLINK, ROOT)
from lectures import Lectures
from utils import recursive_iterdir


class Course():
    def __init__(self, path):
        self.path: Path = path
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

        return CURRENT_COURSE_SYMLINK.resolve()== self.path

    @property
    def relative_path(self):
        return self.path.relative_to(ROOT)

    @staticmethod
    def is_course(path:Path):
        return path.is_dir() and (path / 'info.yaml').exists()

class Courses():

    @staticmethod
    def get_current_course():
        return Course(CURRENT_COURSE_SYMLINK.resolve())
    @staticmethod
    def set_current_course(course:Course):
        CURRENT_COURSE_SYMLINK.unlink()
        CURRENT_COURSE_SYMLINK.symlink_to(course.path)
        CURRENT_COURSE_WATCH_FILE.write_text('{}\n'.format(course.info['short']))

    @staticmethod
    def read_files(path :Path = CURRENT_SEMESTER_SYMLINK):
        """
        Read all courses in path
    
        :param path: path to read courses from
        """
        course_directories = [x for x in recursive_iterdir(path) if x.is_dir() and Course.is_course(x)]
        _courses = [Course(path) for path in course_directories]
        return sorted(_courses, key=lambda c: c.name)

    def __init__(self, path=CURRENT_SEMESTER_SYMLINK):
        self.path = path

    def __iter__(self):
        yield from Courses.read_files(self.path)

    @property
    def current(self):
        return self.get_current_course()

    @current.setter
    def current(self, course):
        self.set_current_course(course)
