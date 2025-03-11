
import os
import gi
# import Glib
from gi.repository import GLib

results = {}

from modules.set_interval import set_interval

def listen_to_directory(directory_paths, event_fn):
    
    def check_changes():
        for directory_path in directory_paths:
            if not os.path.exists(directory_path):

                results[directory_path] = ''
                continue

            ls_result = os.popen('ls -la ' + directory_path).read()

            if directory_path not in results:
                results[directory_path] = ls_result
            else :
                if results[directory_path] != ls_result:
                    # the directory has changed
                    print('Directory changed:', directory_path)
                    event_fn('change', directory_path)
                    results[directory_path] = ls_result

    check_changes()
    set_interval(check_changes, 1)
    


