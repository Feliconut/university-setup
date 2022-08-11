#!/usr/local/bin/python3

from action import Service
from choose_courses import ChooseCurrentCourse
from choose_lectures import ChooseLecture
from choose_lectures_view import ChooseCompileRange
# register all services and options
services = [ChooseCompileRange(),ChooseLecture(),ChooseCurrentCourse()]

class AllChoicesService(Service):
    def __init__(self):
        super().__init__(
            name='ALL',
            description = 'All services, to be invoked by global shortcut')
        self.services = services
        
    def _load_actions(self):
        actions = []
        for service in self.services:
            actions.extend(service.get_available_actions(state))
        return actions



class State():
    pass

state =  State()

if __name__ == '__main__':
    AllChoicesService().execute(state)