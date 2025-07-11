import re

class Prompt:
    @staticmethod
    def ask(prompt, choices=None, default=None, show_default=True):
        # Strip Rich markup from prompt
        clean_prompt = re.sub(r'\[/?[^\]]*\]', '', prompt) if isinstance(prompt, str) else str(prompt)
        
        # Add choices if provided
        if choices:
            choices_str = '/'.join(choices)
            clean_prompt += f" [{choices_str}]"
        
        # Add default if provided and show_default is True
        if default is not None and show_default:
            clean_prompt += f" (default: {default})"
        
        clean_prompt += ": "
        
        while True:
            try:
                response = input(clean_prompt).strip()
                
                # If no input and default is provided, use default
                if not response and default is not None:
                    return default
                
                # If choices are provided, validate the response
                if choices:
                    if response.lower() in [choice.lower() for choice in choices]:
                        return response.lower()
                    else:
                        print(f"Please choose from: {', '.join(choices)}")
                        continue
                
                return response
                
            except (KeyboardInterrupt, EOFError):
                print("\n")
                return default if default is not None else ""


class Confirm:
    @staticmethod
    def ask(prompt, default=False):
        # Strip Rich markup from prompt
        clean_prompt = re.sub(r'\[/?[^\]]*\]', '', prompt) if isinstance(prompt, str) else str(prompt)
        
        # Add y/n indicator
        if default:
            clean_prompt += " [Y/n]: "
        else:
            clean_prompt += " [y/N]: "
        
        try:
            ans = input(clean_prompt).strip()
            if not ans:
                return default
            return ans.lower() in {"y", "yes", "true", "1"}
        except (KeyboardInterrupt, EOFError):
            print("\n")
            return default
