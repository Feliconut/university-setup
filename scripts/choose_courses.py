#!/usr/bin/python3

from courses import courses, Course
from action import Action, MenuItem, Service
from utils import MAX_LEN


class SetCurrentCourse(Action):
    def __init__(self, course: Course):
        self.course = course
        super().__init__(
            name='set current course to {}'.format(course.name),
            display_name='Switch to {name:<{fill}} ({semester})'.format(
                name=course.name,
                fill=MAX_LEN,
                semester=course.semester),
            description='Set the current course')

    def execute(self):
        self.logger.info(
            'Setting current course to {}'.format(self.course.name))
        courses.set_current_course(self.course)


class ChooseCurrentCourse(Service):
    def __init__(self):
        super().__init__(
            name='choose current course',
            description='Choose current course')

    def suggested_actions(self):
        actions = []
        actions += [SetCurrentCourse(course)
                    for course in courses if course is not courses.current]
        return actions


if __name__ == '__main__':
    ChooseCurrentCourse().execute()
