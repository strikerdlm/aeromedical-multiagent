class Text:
    """A simple Text class that mimics Rich's Text functionality."""
    
    def __init__(self, text="", style=None, justify=None, **kwargs):
        """Initialize a Text object.
        
        Args:
            text: The text content
            style: Style to apply (ignored in this simple implementation)
            justify: Text justification (ignored in this simple implementation)
            **kwargs: Additional arguments (ignored)
        """
        self.text = str(text)
        self.style = style
        self.justify = justify
    
    def __str__(self):
        """Return the text content as a string."""
        return self.text
    
    def __repr__(self):
        """Return a representation of the Text object."""
        return f"Text({self.text!r}, style={self.style!r})"
