#!/usr/bin/python3

from courses import Courses, Course
from action import Action, Service
from utils import MAX_LEN


class SetCurrentCourse(Action):
    def __init__(self, course: Course):
        self.course = course
        super().__init__(
            name='Set current course to {}'.format(course.name),
            display_name='Focus on {name:<{fill}} ({semester})'.format(
                name=course.name,
                fill=MAX_LEN,
                semester=course.semester),
            description='Set current course')

    def execute(self):
        self.logger.info(
            'Setting current course to {}'.format(self.course.name))
        Courses.set_current_course(self.course)


class ChooseCurrentCourse(Service):
    def __init__(self):
        super().__init__(
            name='choose course',
            description='Choose current course')

    def suggested_actions(self):
        actions = []
        actions += [SetCurrentCourse(course) for course in Courses()]
        return actions


if __name__ == '__main__':
    ChooseCurrentCourse().execute()
