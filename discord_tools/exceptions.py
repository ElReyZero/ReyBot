class OWException(Exception):

    def __init__(self):
        super().__init__("Outfit Wars is not available at this time. Please try again later.")