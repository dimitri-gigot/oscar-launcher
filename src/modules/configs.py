import os
import json

def get_themes(paths):
    themes = []

    for path in paths:
        if os.path.exists(path):
                # list folder in that folder
                default_themes = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

                # only add it to themes if it does not exist with same name
                for default in default_themes:
                    if not any(d['name'] == default for d in themes):
                        themes.append({'path': os.path.join(path, default, 'style.css'), 'name': default})
    
    # for each theme folder read the style.css file and add it to the object
    for theme in themes:
        with open(theme['path'], 'r') as file:
            theme['css'] = file.read()

    return themes


def get_configs(paths):
    configs = []

    for path in paths:
        if os.path.exists(path):
            # list file in that folder ending with .json
            default_configs = [f for f in os.listdir(path) if f.endswith('.json')]


            # only add it to configs if it does not exist with same name
            for default in default_configs:
                if not any(d['name'] == default for d in configs):
                    configs.append({'path': os.path.join(path, default), 'name': default})

    # for each config file read the content and add it to the object
    for config in configs:
        with open(config['path'], 'r') as file:
            try:
                # json parse the file
                text = file.read()
                config['name'] = config['name'].replace('.json', '')
                config['json'] = json.loads(text)
            except:
                print('Error reading config file:', config['path'])
                config['name'] = config['name'].replace('.json', '')
                config['json'] = json.loads('{"width": 400,"height": 10,"theme": "light","items": [{"type": "text","text": "Error reading config file"}]}')

    # filter out the None values
    configs_final = [c for c in configs if c is not None]

    return configs_final
