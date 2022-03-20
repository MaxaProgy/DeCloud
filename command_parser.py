class CommandParser():
    def __init__(self):
        self._commands = {}

        self._arguments = {}
        self._result = {}

    def add_command(self, name:str):
        self._commands[name] = {}


    def add_argument(self, command, argument, default=None, type=None):
        self._commands[command][argument] = {'default': default, 'type': type}

    def parse_string(self, input_str):
        input_list = input_str.strip().split()
        command_name = input_list.pop(0)
        if command_name not in self._commands:
            return None
        dict_args = {}
        for arg in self._commands[command_name]:
            if arg in input_list:
                dict_args[arg] = input_list[input_list.index(arg) + 1]
            else:
                dict_args[arg] = self._commands[command_name][arg]['default']

        return command_name, dict_args



if __name__ == '__main__':
    par = CommandParser()
    par.add_command('ss')
    par.add_argument('ss', '22', True)
    par.add_argument('ss', '223', False)

    par.add_command('ww')


    print(par.parse_string("ss 22 False 223 True"))
    print(par.parse_string("ss 22 False"))
    print(par.parse_string("ww"))
