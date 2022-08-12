#!/usr/local/bin/python3

from typing import List, Union
from action import Action, MenuItem, Service
from choose_courses import ChooseCurrentCourse, DisplayCurrentCourse
from choose_lectures import ChooseLecture, CreateLectureService
from choose_lectures_view import ChooseCompileRange
from choose_view_pdf import ChooseCoursePDF
# register all services and options
services: List[Union[Service, MenuItem]] = [
    ChooseCompileRange(),
    DisplayCurrentCourse(),
    ChooseLecture(),
    CreateLectureService(),
    ChooseCurrentCourse(),
    ChooseCoursePDF(),
]


class AllChoicesService(Service):
    def __init__(self):
        super().__init__(
            name='ALL',
            description='All services, to be invoked by global shortcut')
        self.services = services

    def suggested_actions(self):
        actions = []
        for service in self.services:
            try:
                actions.extend(service.get_displayed_menuitems())
            except AttributeError:  # is a MenuItem instead of a Service
                assert isinstance(service, MenuItem)
                actions.append(service)
                pass
            except NotImplementedError:
                pass
        return actions

    def action_from_prompt(self, prompt):
        for service in services:
            if isinstance(service, Service):
                try:
                    action: Action = service.action_from_prompt(prompt)
                    if action:
                        return action
                except NotImplementedError:
                    pass


if __name__ == '__main__':
    AllChoicesService().execute()
