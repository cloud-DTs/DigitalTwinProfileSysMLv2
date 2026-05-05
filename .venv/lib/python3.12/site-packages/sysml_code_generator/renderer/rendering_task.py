from dataclasses import dataclass


@dataclass
class RenderingTask:
    template_name: str
    output_filename: str
    variables: any
