import os
import shutil


class Mount:
    link_dir = "l"
    diff_dir_name = "diff"
    work_dir_name = "work"
    merged_dir_name = "merged/"
    lower_file = "lower"
    overlay_path = "/var/lib/docker/overlay2/"
    overlay_name = "overlay"

    def __init__(self):
        pass

    def mount_overlay(self):
        self.remove_overlay_dirs()
        self.create_overlay_dirs()
        directory_diffs = self.get_lower_directories()

        mount_cmd = f"mount -t overlay -o lowerdir={directory_diffs},upperdir=./{self.merged_dir_name},workdir=./{self.work_dir_name} {self.overlay_name} {self.merged_dir_name}/"
        os.chdir(self.overlay_path)
        os.system(mount_cmd)

    def unmount_overlay(self):
        umount_cmd = f"umount {self.overlay_name}"
        os.system(umount_cmd)
        self.remove_overlay_dirs()

    def get_lower_directories(self):
        dirs = os.listdir(self.overlay_path+'/l')
        lower_chain = ""
        for dir in dirs:
            lower_chain += f"l/{dir}:"

        lower_chain = lower_chain[:len(lower_chain)-1]
        return lower_chain

    def remove_overlay_dirs(self):
        if os.path.exists(self.overlay_path + self.diff_dir_name):
            shutil.rmtree(self.overlay_path + self.diff_dir_name)
        if os.path.exists(self.overlay_path + self.work_dir_name):
            shutil.rmtree(self.overlay_path + self.work_dir_name)
        if os.path.exists(self.overlay_path + self.merged_dir_name):
            shutil.rmtree(self.overlay_path + self.merged_dir_name)

    def create_overlay_dirs(self):
        os.makedirs(self.overlay_path + self.diff_dir_name)
        os.makedirs(self.overlay_path + self.work_dir_name)
        os.makedirs(self.overlay_path + self.merged_dir_name)

    @property
    def overlay_root_path(self):
        return self.overlay_path

    @property
    def overlay_mount_path(self):
        return self.overlay_path+self.merged_dir_name

    @property
    def merged(self):
        return self.merged_dir_name
