import yaml

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    print(type(eval(config["camera_resolution"])))

