import abc

import six


@six.add_metaclass(abc.ABCMeta)
class emailHookBase(object):

    def do_action(self, mail_content, sender, receiver):
        raise NotImplementedError
