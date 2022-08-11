#!/usr/local/bin/python3
from courses import Courses

lectures = Courses().current.lectures

commands = ['last', 'prev-last', 'all', 'prev']
cmd_display = ['Current lecture', 'Last two lectures',
           'All lectures', 'Previous lectures']



from courses import Courses, Course
from action import Action,Service


class SetCompileRange(Action):
    def __init__(self, range:str, range_display:str):
        self.range = range
        super().__init__(
            name='Set compile range to {}'.format(self.range),
            display_name='Include {}'.format(range_display),
            description='Set compile range')

    def execute(self, state):
        lecture_range = lectures.parse_range_string(self.range)
        lectures.update_lectures_in_master(lecture_range)
        self.logger.info(self.display_name)
        lectures.compile_master()


class ChooseCompileRange(Service):
    def __init__(self):
        super().__init__(
            name='choose compile range',
            description = 'Choose compile range')

    def _load_actions(self):
        return [SetCompileRange(cmd, disp) for cmd, disp in zip(commands, cmd_display)]

    def improvise_action(self, prompt):
        try:
            lecture_range = lectures.parse_range_string(prompt)
            return SetCompileRange(prompt, 'User entered range: '+ prompt)
        except:
            self.logger.exception('Could not parse range: {}'.format(prompt))

if __name__ == '__main__':
    ChooseCompileRange().execute()
