import os
import subprocess


class Terminal:

    @staticmethod
    def execute_in_unix(script: str):
        return subprocess.check_output(script, shell=True).decode("utf-8")

    @staticmethod
    def execute_in_win(script: str):
        os.system(script)
