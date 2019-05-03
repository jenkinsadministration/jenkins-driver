from libs.terminal import Terminal
import json


class IOS:

    @staticmethod
    def get_simulators_runtime():
        return json.loads(Terminal.execute_in_unix('xcrun simctl list devices --json'))

    @staticmethod
    def get_os_available():
        result = []
        device_types = IOS.get_simulators_runtime()['devices']

        for dt in device_types:
            if str(dt).startswith('iOS '):
                result.append(dt)

        return sorted(result)

    @staticmethod
    def get_available_iphone_simulators(os, device_name=None):
        result = []
        device_types = IOS.get_simulators_runtime()['devices']

        for dt in device_types:

            if str(dt) == os:
                for d in device_types[dt]:
                    if device_name is None or device_name == d['name']:
                        result.append(d)

        return result

    @staticmethod
    def get_latest_os():
        return IOS.get_os_available()[-1]
