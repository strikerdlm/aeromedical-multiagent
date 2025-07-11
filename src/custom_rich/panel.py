import re

class Panel:
    def __init__(self, renderable, title=None, border_style=None, padding=(0, 0)):
        self.renderable = renderable
        self.title = title
        self.border_style = border_style
        self.padding = padding
    
    def __str__(self):
        """Convert Panel to string representation."""
        # Clean up any Rich markup from the renderable content
        if isinstance(self.renderable, str):
            content = re.sub(r'\[/?[^\]]*\]', '', self.renderable)
        else:
            content = str(self.renderable)
        
        # Simple box drawing with title
        lines = content.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        
        # Add padding
        if self.padding:
            pad_vertical, pad_horizontal = self.padding if isinstance(self.padding, tuple) else (self.padding, self.padding)
            lines = [' ' * pad_horizontal + line + ' ' * pad_horizontal for line in lines]
            max_width += 2 * pad_horizontal
            
            # Add vertical padding
            for _ in range(pad_vertical):
                lines.insert(0, ' ' * max_width)
                lines.append(' ' * max_width)
        
        # Create box
        box_width = max_width + 4  # Account for borders
        
        # Top border with title
        if self.title:
            title_clean = re.sub(r'\[/?[^\]]*\]', '', self.title)
            top_line = f"┌─ {title_clean} " + "─" * (box_width - len(title_clean) - 5) + "┐"
        else:
            top_line = "┌" + "─" * (box_width - 2) + "┐"
        
        # Content lines
        content_lines = []
        for line in lines:
            content_lines.append(f"│ {line:<{max_width}} │")
        
        # Bottom border
        bottom_line = "└" + "─" * (box_width - 2) + "┘"
        
        # Combine all lines
        result = [top_line] + content_lines + [bottom_line]
        return '\n'.join(result)
