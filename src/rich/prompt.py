class Prompt:
    @staticmethod
    def ask(prompt, choices=None, default=None):
        return input(f"{prompt} ")


class Confirm:
    @staticmethod
    def ask(prompt, default=False):
        ans = input(f"{prompt} (y/n) ")
        if not ans.strip():
            return default
        return ans.strip().lower() in {"y", "yes"}
