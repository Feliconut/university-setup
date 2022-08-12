#!/usr/local/bin/python3

import os
from pathlib import Path
from shutil import rmtree
from time import sleep

import yaml

from config import (CURRENT_COURSE_ROOT, CURRENT_COURSE_SYMLINK,
                    CURRENT_COURSE_WATCH_FILE, CURRENT_SEMESTER_SYMLINK, ROOT)
from lectures import Lectures
from utils import recursive_iterdir
from vimtex_popup import wait_vim_edit


class Course():
    def __init__(self, path: Path):
        self.path = path
        self.name = path.stem

        self.info = yaml.safe_load((path / 'info.yaml').open())
        self._lectures = []  # lazy loading

    @property
    def lectures(self):
        if not self._lectures:
            self._lectures = Lectures(self)
        return self._lectures

    @property
    def semester(self):
        return self.path.parent.stem

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

    def init_all_course_files(self):
        'Initialize all course files.'
        lectures = self.lectures
        course_title = lectures.course.info["title"]
        lines = [r'%&pdflatex',
                 r'\documentclass[a4paper]{article}',
                 r'\input{../preamble.tex}',
                 fr'\title{{{course_title}}}',
                 r'\begin{document}',
                 r'    \maketitle',
                 r'    \tableofcontents',
                 fr'    % start lectures',
                 fr'    % end lectures',
                 r'\end{document}'
                 ]
        lectures.master_file.touch()
        lectures.master_file.write_text('\n'.join(lines))
        (lectures.root / 'master.tex.latexmain').touch()
        (lectures.root / 'figures').mkdir(exist_ok=True)


class Courses():

    @staticmethod
    def read_current_course():
        'Read the current course from the symlink, and return a new `Course` object'
        try:
            # 'strict = True' means that an exception is raised if the symlink does not exist
            return Course(CURRENT_COURSE_SYMLINK.resolve(strict=True))
        except FileNotFoundError:
            # if there is at least one course, set the current course to the first one
            courses = Courses.read_files(CURRENT_SEMESTER_SYMLINK)
            if len(courses) > 0:
                Courses.set_current_course(courses[0])
                return courses[0]
            else:
                return None

    @staticmethod
    def set_current_course(course: Course):
        'Set the current course symlink to the given course'
        CURRENT_COURSE_SYMLINK.unlink(missing_ok=True)
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

    def __init__(self, semester_path=CURRENT_SEMESTER_SYMLINK):
        self.path = semester_path
        self._courses = []  # lazy loading
        self.read_current_course()  # ensure that the current course is set correctly

    def __iter__(self):
        if not self._courses:
            self._courses = Courses.read_files(self.path)
        yield from self._courses

    @property
    def current(self):
        for course in self:
            if course.is_activated:
                return course
        raise FileNotFoundError(
            'No current course is returned. The semester is empty.')

    @current.setter
    def current(self, course):
        Courses.set_current_course(course)

    def create_course(self, course_name: str):
        'Create a new course in the current semester'

        new_course_path = self.path / course_name
        assert not new_course_path.exists()
        new_course_path.mkdir()
        (new_course_path / 'info.yaml').touch()
        (new_course_path / 'info.yaml').write_text('\n'.join([
            'title: ',
            'short: ',
            'url: ']))
        wait_vim_edit(new_course_path / 'info.yaml')
        sleep(1)  # wait for vim to finish writing and exiting

        course = Course(new_course_path)
        try:
            course.init_all_course_files()  # yaml must have correct syntax
            assert course.info['title'].strip()  # must enter a title
            assert course.info['short'].strip()  # must enter a short name

            Courses.set_current_course(course)
            return course
        except:
            print('Wrong info.yaml')
            rmtree(new_course_path)
            self.create_course(course_name)

    def init_all_course_files(self):
        for course in self:
            course.init_all_course_files()

    def has_current(self):
        try:
            return self.current is not None
        except FileNotFoundError:
            return False


class Semester():
    def __init__(self, path: Path):
        self.path = path
        self.name = path.stem
        self._courses = []  # lazy loading

    def __iter__(self):
        yield from self.courses

    @property
    def courses(self):
        if len(self._courses) == 0:
            self._courses = Courses.read_files(self.path)
        return self._courses

    @property
    def is_current(self):
        return os.path.samefile(self.path, CURRENT_SEMESTER_SYMLINK)

    @property
    def relative_path(self):
        return self.path.relative_to(ROOT)

    @staticmethod
    def is_semester(path: Path):
        if path.is_dir():
            if len(list(filter(lambda x: x.is_dir(), path.iterdir()))) == 0:  # Empty semester
                # empty directory with preamble.tex is a semester
                return (path/'preamble.tex').exists() and not (path / 'master.tex').exists()
            dirs = filter(lambda x: x.is_dir(), path.iterdir())
            for p in dirs:
                if Course.is_course(p):
                    return True  # directory with a course is a semester
        return False


class Semesters():

    @staticmethod
    def read_current_semester():
        'Read the current semester from the symlink, and return a new `Semester` object'
        try:
            # 'strict = True' means that an exception is raised if the symlink does not exist
            return Semester(CURRENT_SEMESTER_SYMLINK.resolve(strict=True))
        except FileNotFoundError:
            # if there is at least one semester, set the current semester to the last one
            semesters = Semesters.read_files()
            if len(semesters) > 0:
                Semesters.set_current_semester(semesters[-1])
                return semesters[-1]
            else:
                return None

    @staticmethod
    def set_current_semester(semester: Semester):
        'Set the current semester symlink to the given semester'
        CURRENT_SEMESTER_SYMLINK.unlink(missing_ok=True)
        CURRENT_SEMESTER_SYMLINK.symlink_to(semester.path)

    @staticmethod
    def read_files():
        """
        Read all semesters in ROOT
        """
        semester_directories = [x for x in recursive_iterdir(
            ROOT) if Semester.is_semester(x)]
        _semesters = [Semester(path) for path in semester_directories]
        return sorted(_semesters, key=lambda s: s.name)

    def __init__(self):
        self._semesters = []  # lazy loading
        self.read_current_semester()  # ensures that the current semester is set correctly

    def __iter__(self):
        if self._semesters == []:
            self._semesters = Semesters.read_files()
        yield from self._semesters

    @property
    def current(self):
        for semester in self:
            if semester.is_current:
                return semester
        raise FileNotFoundError('No current semester')

    @current.setter
    def current(self, semester: Semester):
        Semesters.set_current_semester(semester)

    def has_current(self):
        try:
            return self.current is not None
        except FileNotFoundError:
            return False


# Semesters of the current semester, as a default.
semesters = Semesters()

# Courses of the current semester, as a default.
courses = Courses()
