from action import Action, Service
class ConvertVimtexAction(Action):

    def __init__(self):
        super().__init__(
            name='Convert VimTeX',
            display_name='Convert all VimTeX projects to Logseq',
        )
    def execute(self):
        from logseq_vimtex_link import convert_all
        return convert_all()

if __name__ == '__main__':
    ConvertVimtexAction().execute()