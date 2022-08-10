#!/usr/local/bin/python3

import sys
import iterm2
#import AppKit

# Launch the app
#AppKit.NSWorkspace.sharedWorkspace().launchApplication_("iTerm")
cmd =  (' '.join(sys.argv[1:]) if len(sys.argv) > 1 else None)
async def main(connection):
    app = await iterm2.async_get_app(connection)
    print('get finish')
    # Foreground the app
    await app.async_activate()

    print('activate finish')

    # This will run 'vi' from bash. If you use a different shell, you'll need
    # to change it here. Running it through the shell sets up your $PATH so you
    # don't need to specify a full path to the command.
    print(await iterm2.Window.async_create(connection, command=cmd))


# Passing True for the second parameter means keep trying to
# connect until the app launches.
iterm2.run_until_complete(main, False)
