from ampli_tool.commands import load_package_config

__all__ = ['upload_debian_package', 'build',
           'setup_ubuntu_builder', 'teardown_builder']

from ampli_tool.models import Metadata
from ampli_tool.commands import gen_build_info
from fabric.decorators import task
from fabric.operations import local
from parcel_utils.custom import CustomUbuntu
from parcel_utils.tasks import (
    upload_debian_package, build_package_from_dir,
    setup_ubuntu_builder, teardown_builder,
    vm_connection_settings)
import os
import shutil


@task
def build(tarball_path='.'):
    package_config=load_package_config('../package_config.json')
    with vm_connection_settings():
        build_info = gen_build_info('.', package_config=package_config)
        metadata = Metadata(build_info.package_config.name,
                            build_info.package_config.version,
                            revision=build_info.revision,
                            short_description=build_info.package_config.short_description,
                            dependencies=build_info.package_config.dependencies)
        metadata.vendor = 'mongohg'

        bin_dir = 'usr/bin'
        dirs = [bin_dir]
        for dir_ in dirs:
            if os.path.isdir(dir_):
                shutil.rmtree(dir_)
            os.makedirs(dir_)     
        
        local('tar xf %s' % tarball_path)
        extracted_dir = os.path.basename(tarball_path).replace('.tar.gz', '')
        for bin_ in ['mongo', 'mongod', 'mongoimport', 'mongodump', 'mongoimport', 'mongorestore', 'mongostat']:
            local('cp %s/bin/%s %s/%s' % (extracted_dir, bin_, bin_dir, bin_))

        arch = CustomUbuntu()
        build_package_from_dir(arch, metadata, None,
                               user='root', group='root', run_local=True,
                               prefix='/', source_dirs=['usr'])
