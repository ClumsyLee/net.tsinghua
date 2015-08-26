import yaml

CONFIG_FILENAME = 'config.yml'

def load_config(filename=CONFIG_FILENAME):
    return yaml.load(open(filename, encoding='utf-8'))

def save_config(config, filename=CONFIG_FILENAME):
    yaml.dump(config, open(filename, 'w', encoding='utf-8'),
              default_flow_style=False,
              allow_unicode=True)
