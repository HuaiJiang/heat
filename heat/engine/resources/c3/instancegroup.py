__author__ = 'huajiang'



from heat.openstack.common import log as logging
from heat.engine.resources import autoscaling as autoscaling


logger = logging.getLogger(__name__)


class InstanceGroup(autoscaling.InstanceGroup):

    def _create_template(self, num_instances):
        resource=super(InstanceGroup, self)._create_template(num_instances)
        resource_with_new_key=dict((k.replace(self.name,"instance"),v) for k,v in resource["Resources"].items())
        return {"Resources": resource_with_new_key}


def resource_mapping():
    return {
        'EBAY::C3::InstanceGroup': InstanceGroup
    }