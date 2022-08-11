#!/usr/local/bin/python3

from typing import List
from action import Action, Service
from choose_courses import ChooseCurrentCourse
from choose_lectures import ChooseLecture, CreateLectureService
from choose_lectures_view import ChooseCompileRange
# register all services and options
services:List[Service] = [ChooseCompileRange(),ChooseLecture(), CreateLectureService(),ChooseCurrentCourse()]


class AllChoicesService(Service):
    def __init__(self):
        super().__init__(
            name='ALL',
            description = 'All services, to be invoked by global shortcut')
        self.services = services
        
    def suggested_actions(self):
        actions = []
        for service in self.services:
            actions.extend(service.get_displayed_menuitems())
        return actions

    def action_from_prompt(self, prompt):
        for service in services:
            try:
                action: Action = service.action_from_prompt(prompt)
                if action:
                    return action
            except NotImplementedError:
                pass


if __name__ == '__main__':
    AllChoicesService().execute()