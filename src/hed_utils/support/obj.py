"""
Helper module for inspecting objects in live console session
"""
import inspect
import re
from collections import namedtuple
from typing import List

from tabulate import tabulate

MAX_REPR_LEN = 100

MISSING = object()

AttributeDetails = namedtuple("Attr", "name type is_class is_callable repr doc")


def get_attribute_names(obj, *, private=False, magic=False) -> List[str]:
    """Returns a list of the passed obj's attribute names.

    Arguments:
        obj:        The source object
        private:    Whether or not to include names of private attributes (starting with '_')
        magic:      Should the list include 'magic' (dunder) methods
    """

    def is_magic(name):
        return name.startswith("__")

    def is_private(name):
        return name.startswith("_") and (not is_magic(name))

    def is_normal(name):
        return not (is_magic(name) or is_private(name))

    return [attribute
            for attribute
            in dir(obj)
            if (is_normal(attribute)
                or (magic and is_magic(attribute))
                or (private and is_private(attribute)))]


def get_attribute_details(obj, attribute_name: str, *, try_call=False) -> AttributeDetails:
    """Returns 'AttributeDetails' for desired attribute by name.

    Arguments:
        obj:                The source object
        attribute_name:     Name of the attribute whose details we want.
        try_call:           If set to True, when the attribute is callable,
                            tries to call it and add the result to the details.
    """

    try:
        attribute = getattr(obj, attribute_name, MISSING)
    except BaseException as err:
        return AttributeDetails(attribute_name, None, None, None, "<ERROR-GETTING-ATTRIBUTE>", str(err))

    if attribute is MISSING:
        return AttributeDetails(attribute_name, None, None, None, "<NO-SUCH-ATTR>", None)

    a_type = type(attribute).__name__
    a_is_class = inspect.isclass(attribute)
    a_is_callable = callable(attribute)

    if a_is_callable and try_call:
        try:
            a_repr = repr(attribute())
        except Exception as call_err:
            a_repr = f"[ <CALL ERROR> {call_err} ]"
    else:
        a_repr = repr(attribute)

    if len(a_repr) > MAX_REPR_LEN:
        a_repr = a_repr[:(MAX_REPR_LEN - 3)] + "..."

    a_doc = getattr(attribute, "__doc__", "N/A")
    a_doc = re.sub(r"\s+", " ", str(a_doc))

    return AttributeDetails(
        name=attribute_name,
        type=a_type,
        is_class=("class" if a_is_class else "non-class"),
        is_callable=("callable" if a_is_callable else "non-callable"),
        repr=a_repr,
        doc=a_doc
    )


def format_details(obj, details: List[AttributeDetails]) -> str:
    result = f"Details for object of type: '{type(obj).__name__}'"

    if hasattr(obj, "__name__"):
        result = result + ", __name__: '{}'".format(getattr(obj, "__name__", "N/A"))

    result = result + "\n" + tabulate(
        tabular_data=details,
        headers=["NAME", "TYPE", "IS-CLASS", "IS-CALLABLE", "REPR", "DOC"],
        tablefmt="simple_grid",
        stralign="left",
        floatfmt=".2f",
        missingval="?"
    )

    return result


def print_attributes(obj, *, call_attrs=False, private=False, magic=False):
    """Prints a short table-like summary with details for the given object's attribute.

    This method is to be used in live console session to visually inspect objects.
    """

    a_names = get_attribute_names(obj, private=private, magic=magic)
    a_details = [get_attribute_details(obj, name, try_call=call_attrs) for name in a_names]
    print(format_details(obj, a_details))
