from redmine import Redmine
from redmine.resources import Issue
from redmine.managers import ResourceManager

class RedSample(Redmine):
    def __init__(self, config):
        self.config = config
        super(RedSample, self).__init__(url=config['siteurl'], key=config['apikey'])
        self.custom_resource_paths = (__name__,)

    def __getattr__(self, resource):
        if resource == 'Samples':
            resource = SamplesManager(self, 'Samples')
            resource.resource_class.project_id = self.config['sampleprojectid']
            resource.resource_class.tracker_id = self.config['sampletrackerid']
        else:
            resource = super(RedSample, self).__getattr__(resource)
        return resource

class SamplesManager(ResourceManager):
    def __init__(self, redmine, resource_name):
        self.redmine = redmine
        self.resource_class = Samples
        
class Samples(Issue):
    @classmethod
    def translate_params(cls, params):
        # Inject specific project_id and tracker_id for Samples based on config
        params['project_id'] = cls.project_id
        params['tracker_id'] = cls.tracker_id
        return super(Samples, cls).translate_params(params)
