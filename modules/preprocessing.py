import docker
import re, os
from pathlib import Path


class PreProcessing:
    image = None
    img_meta = None
    action_dict = {
        "ADD": False,
        "COPY": False,
        "openssl": False,
        "wget": False,
        "git clone": False,
        "ssh-keygen": False,
    }
    target_dirs = set()
    workdir = "/"
    #   initialize environment

    def __init__(self, img_name):
        self.client = docker.from_env()
        self.img_name = img_name

    #   updates action_dict which actions are found in img_meta_data
    def contains_key_actions(self):
        for key in self.action_dict.keys():
            if key in self.img_meta:
                self.action_dict.update({key: True})

        for value in self.action_dict.values():
            if value is True:
                return True

        return False

    #   collects meta_data of the image
    def collect_metadata(self):
        self.image = self.client.images.get(self.img_name)
        self.img_meta = str(self.image.history())

    #   set targets for ADD, COPY and RUN
    def determine_targets(self):
        for target in self.fetch_direct_copy_targets():
            self.target_dirs.add(target)

        for target in self.fetch_indirect_copy_targets():
            self.target_dirs.add(target)

        if None in self.target_dirs:
            self.target_dirs.remove(None)

        if './' in self.target_dirs:
            self.target_dirs.remove('./')

    #   set targets for ADD and COPY
    def fetch_direct_copy_targets(self):
        self.workdir = '/'
        temp_set = set()
        for match in re.finditer("(dir|file):[a-f0-9]{64}\sin\s", self.img_meta):
            target_path = self.img_meta[match.span()[1]:self.img_meta.find("'", match.span()[1]) - 1]
            search_pattern_until_this_pos = match.span()[0]
            temp_meta = self.img_meta[search_pattern_until_this_pos:]

            self.examine_workdir(temp_meta)

            if target_path is '/':
                continue

            temp_set.add(self.deal_with_path(target_path))
        return temp_set

    #   set targets for RUN
    def fetch_indirect_copy_targets(self):
        self.workdir = '/'
        temp_set = set()
        for match in re.finditer("(/bin/sh\s-c|&&)\s(openssl genrsa|wget|git clone|ssh-keygen)", self.img_meta):
            start_pos = match.span()[0]
            if "openssl" in match.group():
                temp_set.add(self.get_openssl_output_folder(start_pos))

            if "wget" in match.group():
                temp_set.add(self.get_wget_output_folder(start_pos))

            if "git clone" in match.group():
                temp_set.add(self.get_git_output_folder(start_pos))

            if "ssh-keygen" in match.group():
                temp_set.add(self.get_sshkeygen_output_folder(start_pos))
        return temp_set

    #   EXAMINATION OF SPECIFIC UTILS AREA
    #
    #
    #
    #   examines openssl params
    def get_openssl_output_folder(self, start_pos):
        openssl_option = '-out'
        return self.examine_with_specific_option(openssl_option, start_pos)

    #   examines wget params
    def get_wget_output_folder(self, start_pos):
        wget_option = '-O'
        return self.examine_with_specific_option(wget_option, start_pos)

    #   examines git clone params
    def get_git_output_folder(self, start_pos):
        init_string = self.img_meta[start_pos:]
        repo_pattern = '(\w+://)(.+@)*([\w\d\.]+)(:[\d]+){0,1}/*(.*)'
        match = re.search(repo_pattern, init_string)

        end_pos_cmd = init_string.find("'")

        examine_string = init_string[match.span()[0]:end_pos_cmd]
        if " " not in examine_string:
            examine_string = "/"
        else:
            space_pos = examine_string.find(" ")
            examine_string = examine_string[space_pos + 1:len(examine_string)]

        return examine_string

    #   examines sshkeygen params
    def get_sshkeygen_output_folder(self, start_pos):
        keygen_option = '-f'
        return self.examine_with_specific_option(keygen_option, start_pos)

    #   helper for repeated recur
    #
    #
    #
    def examine_with_specific_option(self, option, pos):
        keygen_option_pos = self.img_meta.find(option, pos)
        if keygen_option_pos is -1:
            return self.workdir
        target_path = self.img_meta[keygen_option_pos:]

        #  find 'option' -> start at pos of len(option) and create a substring to whitespace
        end_pos_temp_string = target_path.find(' ', len(option) + 1)
        target_path = target_path[len(option) + 1:end_pos_temp_string]
        if ',' in target_path:
            target_path = target_path[:-2]

        temp_meta = self.img_meta[:keygen_option_pos]
        self.examine_workdir(temp_meta)
        return self.deal_with_path(target_path)

    def examine_workdir(self, meta_temp):
        match = re.search("WORKDIR", meta_temp)
        if match is not None:
            temp_workdir = meta_temp[match.span()[1]+1:meta_temp.find("'", match.span()[1])]
            if temp_workdir[len(temp_workdir)-1] == '/':
                temp_workdir = temp_workdir[:len(temp_workdir)-1]
            self.workdir = temp_workdir
        else:
            self.workdir = "/"

    def deal_with_path(self, target_path):
        if target_path[0] is '~':
            return '/root'
        if target_path[0] is '/':
            return target_path
        if target_path[0] is '.':
            return self.workdir
        elif target_path[0] is not '/' and target_path[0] is not '.':
            return str((self.workdir + '/' + target_path).replace('//', '/'))

    @property
    def targets(self):
        return self.target_dirs
