from .data_models import Voice, VoiceClip, Source
import yaml
import logging

def yaml_to_dataclass(yaml_file: str):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    name = data.get("name")
    description = data.get("description")

    clips = []

    for key, info in data.items():
        if key in ["name", "description"]:
            continue

        source_data = info.get("source", {})

        source = Source(
            location=source_data.get("location"),
            type=source_data.get("type"),
            start_time=source_data.get("start_time"),
            end_time=source_data.get("end_time")
        )

        voice_clip = VoiceClip(
            name=name,
            idx=int(key),
            description=description,
            source=source,
            isolate=info.get("isolate"),
            clip_size=info.get("clip_size")
        )
        clips.append(voice_clip)

    return Voice(name=name, description=description, clips=clips)


import logging

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to the console handler
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    return logger
import logging

def init_logger(log_level=logging.INFO):
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])