import logging

from hed_utils.selenium import defaults

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


class LocatorWrapper:
    def __init__(self, by, value, timeout=None, visible_only=None, required=None, desc=None):
        self.by = by
        self.value = value
        self.timeout = float(defaults.ELEMENT_WAIT_TIMEOUT if timeout is None else timeout)
        self.visible_only = True if visible_only is None else visible_only
        self.required = True if required is None else required
        self.desc = "N/A" if desc is None else desc

    def __repr__(self):
        return ("LocatorWrapper(by='%s', value='%s', timeout=%d, visible_only=%s, required=%s, desc='%s')" %
                (self.by, self.value, self.timeout, self.visible_only, self.required, self.desc))
