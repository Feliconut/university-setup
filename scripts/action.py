import logging
from sre_parse import State


# Creating and Configuring Logger

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(
    filename = "/Users/xiaoyu/Repos/university-setup/scripts/logfile.log",
    # stream=sys.stdout,
    filemode="w",
    format=Log_Format,
    level=logging.DEBUG)


class Loggable():
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)


class Action(Loggable):
    def __init__(self, name, display_name=None, description=None, *args):
        super().__init__()
        self.name = name  # internal name
        # name as displayed in the menu, may be altered
        self.display_name = display_name if display_name else name
        self.description = description
        self.args = args

    def execute(self, *args):
        raise NotImplementedError()

    def __str__(self):
        return self.name + ' ' + self.description + ' ' + str(self.args)


class Service(Loggable):
    def __init__(self, name, description, *args):
        super().__init__()
        self.name = name
        self.description = description
        self.actions = []
        self.args = args

    def _load_actions(self):
        raise NotImplementedError()

    def __str__(self):
        return self.name + ' ' + self.description + ' ' + str(self.actions)

    def get_available_actions(self, state):
        try:
            new_actions = self._load_actions()
            assert isinstance(new_actions, list)
            self.actions = new_actions
        except:
            self.logger.warning(
                'Could not load actions for service {}'.format(self.name))
            pass
        return self.actions
    
    def improvise_action(self, prompt):
        raise NotImplementedError()

    def execute(self, state: State = None):
        from choose import Choose
        available_actions = self.get_available_actions(state)

        returncode, index, selected = Choose.run(
            'Select option', [action.display_name for action in available_actions], [])
        # parse the result, send to service process

        if returncode is Choose.CODE.SELECTED:
            if index == -1:
                try:
                    action = self.improvise_action(selected)
                    if action:
                        action.execute(state)
                except NotImplementedError:
                    pass
            else:
                action = available_actions[index]
                action.execute(state)

            

