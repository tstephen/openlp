class Renderer(object):
    """
    The renderer builds up a web page and then passes it on to the Display to show
    """
    def __init__(self, displays=None):
        """
        Set up the renderer
        """
        self.displays = displays if displays else []
        self.scripts = []
        self.styles = []

    def add_display(self, display):
        """
        Add a display to the renderer.

        The renderer will render the HTML, Javascript and CSS and send it to all of its displays
        """
        self.displays.append(display)

    def add_javascript(self, script):
        """
        Add Javascript to the slide
        """
        pass
