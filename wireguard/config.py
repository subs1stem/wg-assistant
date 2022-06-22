class Config:
    def __init__(self, config: str):
        self.config = config

    def parse_config(self):
        lines = map(lambda line: line.replace('\n', ''),
                    self.config.split('\n\n'))
        print(lines)
