#!/usr/bin/env python
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime
from distutils.version import LooseVersion
import errno
import logging
import os
import pkg_resources
import subprocess
import sys


VAR_PATH = '/var/lib/heat-cfntools'
LOG = logging.getLogger('heat-provision')


def chk_ci_version():
    v = LooseVersion(pkg_resources.get_distribution('cloud-init').version)
    return v >= LooseVersion('0.6.0')


def init_logging():
    LOG.setLevel(logging.INFO)
    LOG.addHandler(logging.StreamHandler())
    fh = logging.FileHandler("/var/log/heat-provision.log")
    os.chmod(fh.baseFilename, 0o600)
    LOG.addHandler(fh)


def call(args):

    class LogStream(object):

        def write(self, data):
            LOG.info(data)

    LOG.info('%s\n', ' '.join(args))  # noqa
    try:
        ls = LogStream()
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        data = p.communicate()
        if data:
            for x in data:
                ls.write(x)
    except OSError as ex:
        if ex.errno == errno.ENOEXEC:
            LOG.error(_('Userdata empty or not executable: %s'), ex)
            return os.EX_OK
        else:
            LOG.error(_('OS error running userdata: %s'), ex)
            return os.EX_OSERR
    except Exception as ex:
        LOG.error(_('Unknown error running userdata: %s'), ex)
        return os.EX_SOFTWARE
    return p.returncode


def main():

    if not chk_ci_version():
        # pre 0.6.0 - user data executed via cloudinit, not this helper
        LOG.error(_('Unable to log provisioning, need a newer version of'
                    ' cloud-init'))
        return -1

    userdata_path = os.path.join(VAR_PATH, 'cfn-userdata')
    os.chmod(userdata_path, 0o700)

    LOG.info(_('Provision began: %s'), datetime.datetime.now())
    returncode = call([userdata_path])
    LOG.info(_('Provision done: %s'), datetime.datetime.now())
    if returncode:
        return returncode


if __name__ == '__main__':
    init_logging()

    code = main()
    if code:
        LOG.error(_('Provision failed with exit code %s'), code)
        sys.exit(code)

    provision_log = os.path.join(VAR_PATH, 'provision-finished')
    # touch the file so it is timestamped with when finished
    with file(provision_log, 'a'):
        os.utime(provision_log, None)
