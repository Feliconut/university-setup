import logging
import sys


# Creating and Configuring Logger

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(
    # filename="/Users/xiaoyu/Repos/university-setup/scripts/logfile.log",
    stream=sys.stdout,
    filemode="w",
    format=Log_Format,
    level=logging.DEBUG)


class Loggable():
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)


class Describable():
    def __init__(self):
        pass

    @property
    def description(self):
        if self.__class__.__doc__:
            return self.__class__.__doc__
        else:
            return self.__class__.__name__ + 'has no description'


class MenuItem(Describable):
    def __init__(self, name, display_name=None, ):
        self.name = name  # internal name
        # name as displayed in the menu, may be altered
        self.display_name = display_name if display_name else name

    def __str__(self):
        return self.name + ' ' + self.description


class Action(Loggable, MenuItem):
    def __init__(self, name, display_name=None):
        Loggable.__init__(self)
        MenuItem.__init__(self, name, display_name)

    def execute(self):
        raise NotImplementedError()


class Service(Loggable, Describable):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.actions = []
        self.hint_word = []

    def suggested_actions(self):
        raise NotImplementedError()

    def __str__(self):
        return self.name + ' ' + self.description + ' ' + str(self.actions)

    def get_displayed_menuitems(self, include_hint=True):
        try:
            new_actions = self.suggested_actions()
            assert isinstance(new_actions, list)
            self.actions = new_actions
        except NotImplementedError:
            self.actions = []
        except:
            self.logger.warning(
                'Failed to load suggested actions for service {}'.format(self.name))
            pass

        if include_hint and self.hint_word:
            # add a empty action according to hint word
            hint_prompt = ' '.join(self.hint_word)
            hint_action = MenuItem(hint_prompt, hint_prompt)
            return self.actions + [hint_action]
        else:
            return self.actions

    def make_custom_action(self, args: list):
        raise NotImplementedError()

    def action_from_prompt(self, prompt: str):
        args = prompt.strip().split()
        try:
            if self.hint_word == args[:len(self.hint_word)]:
                action = self.make_custom_action(
                    args[len(self.hint_word):])
                return action
        except IndexError:
            pass
        except NotImplementedError:
            pass

    def execute(self):
        from choose import Choose
        available_menuitems = self.get_displayed_menuitems()

        options = [action.display_name for action in available_menuitems]
        # options += [' '.join(self.hint_word)]
        returncode, index, selected = Choose.run(
            'Select option', options, [])
        # parse the result, send to service process

        if returncode is Choose.CODE.SELECTED:
            if index != -1:
                menuitem = available_menuitems[index]

                if isinstance(menuitem, Action):
                    return menuitem.execute()
            action = self.action_from_prompt(selected)
            if action:
                action.execute()
