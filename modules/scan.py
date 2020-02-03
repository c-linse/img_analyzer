from modules.mount import Mount
import os


class Scan:
    root_dirs = ""

    def __init__(self, target_list):
        self.target_list = target_list
        self.root_dirs = self.get_root_diff()

        pass

    def output(self):
        print("Output")

    def scan_for_rsa_pk(self):

        mount = Mount()
        fix_strings = ["-----BEGIN OPENSSH PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY-----",
                       "-----BEGIN PRIVATE KEY-----"]
        for prefix in fix_strings:
            for dir in self.target_list:
                if dir is '/':
                    for target_root in self.get_root_diff():
                        os.system(f"find {mount.overlay_mount_path + '/' + target_root} -type f -iname '*' -exec grep -HIr -- '{prefix}' "'{}'" \;")
                else:
                    os.system(f"find {mount.overlay_mount_path + dir} -type f -iname '*' -exec grep -HIr -- '{prefix}' "'{}'" \;")

    def scan_for_aws_key(self):
        mount = Mount()
        aws_pattern = "AKIA[0-9A-Z]\{16\}"
        for dir in self.target_list:
            if dir is '/':
                for target_root in self.get_root_diff():
                    os.system(f"find {mount.overlay_mount_path + '/' + target_root} -type f -iname '*' -exec grep -HIre '{aws_pattern}' "'{}'" \;")
            else:
                os.system(f"find {mount.overlay_mount_path + dir} -type f -iname '*' -exec grep -HIre '{aws_pattern}' "'{}'" \;")

    def get_root_diff(self):
        mount = Mount()
        lst1 = {"bin", "boot", "cdrom", "dev", "etc", "home", "initrd.img", "initrd.img.old", "lib", "lib64",
                "lost+found", "media", "mnt", "opt", "proc", "root", "run", "sbin", "snap", "srv", "swapfile", "sys",
                "tmp", "usr", "var", "vmlinuz", "vmlinuz.old"}

        lst2 = set()
        for d in os.listdir(mount.overlay_mount_path):
            lst2.add(d)

        return self.diff(lst2, lst1)

    def diff(self, first, second):
        second = set(second)
        return [item for item in first if item not in second]