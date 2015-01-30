from __future__ import unicode_literals

from prompt_toolkit.completion import Completer, Completion
import os

__all__ = (
    'PathCompleter',
)


class PathCompleter(Completer):
    """
    Complete for Path variables.

    :param get_paths: Callable which returns a list of directories to look into
                      when the user enters a relative path.
    :param file_filter: Callable which takes a filename and returns whether
                        this file should show up in the completion. ``None``
                        when no filtering has to be done.
    :param min_input_len: Don't do autocompletion when the input string is shorter.
    """
    def __init__(self, only_directories=False, get_paths=None, file_filter=None,
                 min_input_len=0):
        assert get_paths is None or callable(get_paths)
        assert file_filter is None or callable(file_filter)
        assert isinstance(min_input_len, int)

        self.only_directories = only_directories
        self.get_paths = get_paths or (lambda: ['.'])
        self.file_filter = file_filter or (lambda _: True)
        self.min_input_len = min_input_len

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        # Complete only when we have at least the  minimal input length,
        # otherwise, we can too many results and autocompletion will become too
        # heavy.
        if len(text) < self.min_input_len:
            return

        try:
            dirname = os.path.dirname(text)
            directories = [os.path.dirname(text)] if dirname else self.get_paths()
            prefix = os.path.basename(text)

            # Get all filenames.
            filenames = []
            for directory in directories:
                for filename in os.listdir(directory):
                    if filename.startswith(prefix):
                        filenames.append((directory, filename))

            # Sort
            filenames = sorted(filenames, key=lambda k: k[1])

            # Yield them.
            for directory, filename in filenames:
                completion = filename[len(prefix):]
                full_name = os.path.join(directory, filename)

                if not os.path.isdir(full_name):
                    if self.only_directories or not self.file_filter(full_name):
                        continue

                yield Completion(completion, 0, display=filename,
                                 get_display_meta=self._create_meta_getter(full_name))
        except OSError:
            pass

    def _create_meta_getter(self, full_name):
        """
        Create lazy meta getter.
        """
        def getter():
            if os.path.isdir(full_name):
                return 'Directory'
            elif os.path.isfile(full_name):
                return 'File'
            elif os.path.islink(full_name):
                return 'Link'
            else:
                return ''
        return getter