import yaml


def read_config(file_path):
    with open(file_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        return config
    

def str2bool(v):
  return str(v).strip().lower() in ( "yes", "true", "t", "1", "y" )
