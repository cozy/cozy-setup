# Module:   help
# Date:     28th November 2013
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""Help Tasks"""


from __future__ import print_function


from fabric import state
from fabric.api import task
from fabric.tasks import Task
from fabric.task_utils import crawl


@task(default=True)
def help(name=None):
    """Display help for a given task

    Options:
        name    - The task to display help on.

    To display a list of available tasks type:

        $ fab -l

    To display help on a specific task type:

        $ fab help:<name>
    """

    if name is None:
        name = "help"

    task = crawl(name, state.commands)
    if isinstance(task, Task):
        doc = getattr(task, "__doc__", None)
        if doc is not None:
            print("Help on {0:s}:".format(name))
            print()
            print(doc)
        else:
            print("No help available for {0;s}".format(name))
    else:
        print("No such task {0:s}".format(name))
        print("For a list of tasks type: fab -l")
