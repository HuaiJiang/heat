__author__ = 'huajiang'

from heat.openstack.common import log as logging
from heat.engine.resources import instance as ec2instance


logger = logging.getLogger(__name__)


class Instance(ec2instance.Instance):

    def __init__(self, name, json_snippet, stack):
        super(Instance, self).__init__(name, json_snippet, stack)


    def physical_resource_name(self):
        if self.id is None:
            return None

        name = '%s-%s' % (self.stack.name,
                             self.name)

        if self.physical_resource_name_limit:
            name = self.reduce_physical_resource_name(
                name, self.physical_resource_name_limit)
        return name







def resource_mapping():
    return {
        'EBAY::C3::Instance': Instance
    }