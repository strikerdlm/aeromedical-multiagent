import re

class Table:
    def __init__(self, title=None, *args, **kwargs):
        self.title = title
        self.columns = []
        self.rows = []
        self.is_grid = kwargs.get('grid', False)
        self.padding = kwargs.get('padding', 0)
    
    def add_column(self, header=None, style=None, width=None, justify="left", *args, **kwargs):
        """Add a column to the table."""
        # Strip Rich markup from header
        if header is not None:
            clean_header = re.sub(r'\[/?[^\]]*\]', '', header) if isinstance(header, str) else str(header)
        else:
            clean_header = ""
        self.columns.append({
            'header': clean_header,
            'style': style,
            'width': width,
            'justify': justify
        })
    
    def add_row(self, *row_data, **kwargs):
        """Add a row to the table."""
        # Strip Rich markup from each cell
        clean_row = []
        for cell in row_data:
            if isinstance(cell, str):
                clean_cell = re.sub(r'\[/?[^\]]*\]', '', cell)
            else:
                clean_cell = str(cell)
            clean_row.append(clean_cell)
        self.rows.append(clean_row)
    
    def __str__(self):
        """Render the table as a string."""
        if not self.columns:
            return ""
        
        # Handle grid tables (no borders)
        if self.is_grid:
            result = []
            for row in self.rows:
                padded_row = []
                for i, cell in enumerate(row):
                    if i < len(self.columns):
                        cell_str = str(cell)
                        if self.padding:
                            cell_str = ' ' * self.padding + cell_str + ' ' * self.padding
                        padded_row.append(cell_str)
                result.append(''.join(padded_row))
            return '\n'.join(result)
        
        # Calculate column widths
        widths = []
        for i, col in enumerate(self.columns):
            if col['width']:
                widths.append(col['width'])
            else:
                # Calculate width based on content
                col_width = len(col['header'])
                for row in self.rows:
                    if i < len(row):
                        col_width = max(col_width, len(str(row[i])))
                widths.append(col_width)
        
        # Build the table
        result = []
        
        # Title
        if self.title:
            clean_title = re.sub(r'\[/?[^\]]*\]', '', self.title)
            total_width = sum(widths) + len(widths) * 3 + 1
            title_line = f"┌─ {clean_title} " + "─" * (total_width - len(clean_title) - 5) + "┐"
            result.append(title_line)
        
        # Header
        header_row = "│"
        for i, col in enumerate(self.columns):
            width = widths[i]
            header_cell = f" {col['header']:<{width}} "
            header_row += header_cell + "│"
        result.append(header_row)
        
        # Header separator
        separator = "├"
        for width in widths:
            separator += "─" * (width + 2) + "┼"
        separator = separator[:-1] + "┤"
        result.append(separator)
        
        # Data rows
        for row in self.rows:
            row_str = "│"
            for i, cell in enumerate(row):
                if i < len(widths):
                    width = widths[i]
                    cell_str = str(cell)
                    if i < len(self.columns):
                        justify = self.columns[i]['justify']
                        if justify == "right":
                            cell_formatted = f" {cell_str:>{width}} "
                        elif justify == "center":
                            cell_formatted = f" {cell_str:^{width}} "
                        else:
                            cell_formatted = f" {cell_str:<{width}} "
                    else:
                        cell_formatted = f" {cell_str:<{width}} "
                    row_str += cell_formatted + "│"
            result.append(row_str)
        
        # Bottom border
        bottom = "└"
        for width in widths:
            bottom += "─" * (width + 2) + "┴"
        bottom = bottom[:-1] + "┘"
        result.append(bottom)
        
        return '\n'.join(result)
    
    @staticmethod
    def grid(*args, **kwargs):
        """Create a grid table (no borders)."""
        table = Table(*args, **kwargs)
        table.is_grid = True
        return table
