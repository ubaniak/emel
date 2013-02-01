def yes_no_option(message):
    choice = raw_input('\n' + message + '(y/N)')
    while choice.lower() != 'y' and choice.lower() != 'n' and choice != '':
        choice = raw_input( 'Invalid input please enter (y/N): ' )

    return True if choice == 'y' else False
