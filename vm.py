

"""Start Google Cloud Computing VM Instances programmatically.
   This works with a setup where a relay instance is used to access the
   GPU instance: LAPTOP -> RELAY -> GPU

   NOTE: Requires gcloud command to be installed and configured.
         gcloud config --help

   HOWTO USE:
       python vm.py start
       ssh bubblehawk
       python vm.py stop
"""

import os
import re
import argparse
import subprocess

GPU_INSTANCE = "bubblehawk"
GPU_PROJECT = "artistsandmachines"
GPU_ZONE = "us-west1-b"

RELAY_INSTANCE = "teslafink"
RELAY_PROJECT = "tensorfoo"
RELAY_ZONE = "europe-west1-b"

relay_params = (RELAY_INSTANCE, RELAY_PROJECT, RELAY_ZONE)
gpu_params = (GPU_INSTANCE, GPU_PROJECT, GPU_ZONE)


def start():
    """Start both vm instances and write the IP addresses to .ssh/config on
    this computer and RELAY computer. Then you can use the oProxyJump ssh
    argument to access the GPU VM:

    scp -oProxyJump=teslafink test.pdf  bubblehawk:~/

    OR with a .ssh/config entry like this also directly:

    Host bubblehawk
        HostName 35.185.214.138
        user stefan
        IdentityFile ~/.ssh/google-gce-ssh-key
        ProxyCommand ssh teslafink nc %h %p
    """
    cmd = "gcloud compute instances start %s --project %s --zone %s" % relay_params
    os.system(cmd)
    cmd = "gcloud compute instances start %s --project %s --zone %s" % gpu_params
    os.system(cmd)
    # set SSH config file on LAPTOP and RELAY with IP from GPU_INSTANCE
    gpu_ip = get_gpu_ip()
    relay_ip = get_relay_ip()
    replace_ip_in_ssh_config('~/.ssh/config', RELAY_INSTANCE, relay_ip)
    replace_ip_in_ssh_config('~/.ssh/config', GPU_INSTANCE, gpu_ip)
    update_remote_ssh_ip(RELAY_INSTANCE, GPU_INSTANCE, gpu_ip)

def stop():
    cmd = "gcloud compute instances stop %s --project %s --zone %s" % relay_params
    os.system(cmd)
    cmd = "gcloud compute instances stop %s --project %s --zone %s" % gpu_params
    os.system(cmd)





def get_relay_ip():
    cmd = 'gcloud compute instances list --filter=%s --project=%s --format="value(networkInterfaces[0].accessConfigs[0].natIP)"' % (RELAY_INSTANCE, RELAY_PROJECT)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = p.communicate()
    return out.strip()

def get_gpu_ip():
    cmd = 'gcloud compute instances list --filter=%s --project=%s --format="value(networkInterfaces[0].accessConfigs[0].natIP)"' % (GPU_INSTANCE, GPU_PROJECT)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = p.communicate()
    return out.strip()


def update_remote_ssh_ip(host, host_entry, ip):
    selfname = __file__[:-3]
    os.system('scp %s %s:~/' % (os.path.abspath(__file__), host))
    pycode = "import %s; %s.replace_ip_in_ssh_config('~/.ssh/config', '%s', '%s')" % (selfname, selfname, host_entry, ip)
    call_remote_python(host, pycode)
    os.system('ssh %s "rm %s; rm %sc"' % (host, __file__, __file__))

def call_remote_python(host, pythoncode):
    """Execute remote python.
    NOTE: Only use single quotes in pythoncode."""
    cmd = 'ssh %s "python -c \\\"%s\\\""' % (host, pythoncode)
    os.system(cmd)


def replace_ip_in_ssh_config(file_path, host, new_ip):
    """Edit IP entry in .ssh/config
    Expects an entry like this:
    ---------------------------
    Host bubblehawk
        HostName 35.185.214.138
        User stefan
        IdentityFile ~/.ssh/google-gce-ssh-key
    ---------------------------
    """
    file_path = os.path.expanduser(file_path)
    fp = open(file_path)
    config_str = fp.read()
    new_str = re.sub('Host '+host+'\n    HostName ([0-9]{1,3}\.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3})\n',
                     'Host %s\n    HostName %s\n' % (host, new_ip), config_str)
    fp.close()
    fp = open(file_path, 'w')
    fp.write(new_str)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=['start', 'stop'])
    args = parser.parse_args()

    if args.cmd == 'start':
        start()
    elif args.cmd == 'stop':
        stop()

    # list status
    os.system("gcloud compute instances list --project %s" % (RELAY_PROJECT))
    os.system("gcloud compute instances list --project %s" % (GPU_PROJECT))
