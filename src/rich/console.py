import re

class Console:
    def print(self, *args, **kwargs):
        # Convert args to strings and strip Rich markup
        cleaned_args = []
        for arg in args:
            if isinstance(arg, str):
                # Remove Rich markup tags like [bold], [dim], [green], etc.
                cleaned = re.sub(r'\[/?[^\]]*\]', '', arg)
                cleaned_args.append(cleaned)
            else:
                cleaned_args.append(arg)
        
        # Use the built-in print function with cleaned args
        print(*cleaned_args, **kwargs)
    
    def status(self, text, spinner="dots"):
        """Simple status context manager that just prints the text."""
        class StatusContext:
            def __init__(self, text):
                self.text = text
                
            def __enter__(self):
                print(f"⏳ {self.text}")
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
                
        return StatusContext(text)
