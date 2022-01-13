#!/usr/bin/python3
"""A module for web application deployment with Fabric."""
import fabric.api as fabric_api
import os
from datetime import datetime


fabric_api.env.hosts = ["34.73.0.174", "34.75.208.81"]
"""The list of host server IP addresses."""
fabric_api.env.user = "ubuntu"
"""The username of the host servers."""


@fabric_api.runs_once
def do_pack():
    """Archives the static files."""
    if not os.path.isdir("versions"):
        os.mkdir("versions")
    cur_time = datetime.now()
    output = "versions/web_static_{}{}{}{}{}{}.tgz".format(
        cur_time.year,
        cur_time.month,
        cur_time.day,
        cur_time.hour,
        cur_time.minute,
        cur_time.second
    )
    try:
        print("Packing web_static to {}".format(output))
        fabric_api.local("tar -cvzf {} web_static".format(output))
        archize_size = os.stat(output).st_size
        print("web_static packed: {} -> {} Bytes".format(output, archize_size))
    except Exception:
        output = None
    return output


def do_deploy(archive_path):
    """Deploys the static files to the host servers.
    Args:
        archive_path (str): The path to the archived static files.
    """
    if not os.path.exists(archive_path):
        return False
    file_name = os.path.basename(archive_path)
    folder_name = file_name.replace(".tgz", "")
    folder_path = "/data/web_static/releases/{}/".format(folder_name)
    success = False
    try:
        fabric_api.put(archive_path, "/tmp/{}".format(file_name))
        fabric_api.run("mkdir -p {}".format(folder_path))
        fabric_api.run(
            "tar -xzf /tmp/{} -C {}".format(file_name, folder_path)
        )
        fabric_api.run("rm /tmp/{}".format(file_name))
        fabric_api.run(
            "mv {}web_static/* {}".format(folder_path, folder_path)
        )
        fabric_api.run("rm -rf {}web_static".format(folder_path))
        fabric_api.run("rm -rf /data/web_static/current")
        fabric_api.run(
            "ln -sf {} /data/web_static/current".format(folder_path)
        )
        success = True
    except Exception:
        success = False
    return success


def deploy():
    """Archives and deploys the static files to the host servers.
    """
    archive_path = do_pack()
    return do_deploy(archive_path) if archive_path else False


def do_clean(number=0):
    """Deletes out-of-date archives of the static files.
    Args:
        number (Any): The number of archives to keep.
    """
    archives = os.listdir('versions/')
    archives.sort(reverse=True)
    start = int(number)
    if start < len(archives):
        archives = archives[start:]
    else:
        archives = []
    for archive in archives:
        os.unlink('versions/{}'.format(archive))
    cmd_parts = [
        "rm -Rf $(",
        "find /data/web_static/releases/ -maxdepth 1 -type d -iregex",
        " '/data/web_static/releases/web_static_.*'",
        " | sort -r | tr '\\n' ' ' | cut -d ' ' -f{}-)".format(start + 1)
    ]
    fabric_api.run(''.join(cmd_parts))
