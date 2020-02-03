import sys
sys.path.append('/Users/clinse/Documents/dev/python/image_scan/img_back')
sys.path.append('/mnt/python/image_scan/img_back')
import os
import timeit
from modules.obtain import ImgObtain
from modules.preprocessing import PreProcessing
from modules.mount import Mount
from modules.scan import Scan


class AnalManager:
    necessary = False
    target_list = list()

    def __init__(self, img_name):
        self.img_name = img_name
        self.img_obtain = ImgObtain(img_name)
        self.img_preprocessor = PreProcessing(img_name)

    def prepare_environment(self):
        mount = Mount()
        print(f"#"*5 + "   Stopping possible Containers   " + "#"*5 + "\n")
        self.img_obtain.stop_all_containers()
        print(f"#"*5 + "   Unmounting old images   " + "#"*5 + "\n")
        mount.unmount_overlay()
        print(f"#"*5 + "   Removing old images   " + "#"*5 + "\n")
        #self.img_obtain.remove_old_images()
        print(f"#"*5 + "   Pulling image   " + str({self.img_name}) + "#"*5 + "\n")
        #self.img_obtain.pull_image()

    def preprocess(self):
        self.img_preprocessor.collect_metadata()
        if self.img_preprocessor.contains_key_actions():
            self.necessary = True
            self.img_preprocessor.determine_targets()
            self.target_list = self.img_preprocessor.targets

    def mount(self):
        mount = Mount()
        mount.mount_overlay()

    def examine_deeply(self):

        scan = Scan(self.target_list)

        print(f"#"*5 + "   examination RSA keys starts   " + "#"*5)
        scan.scan_for_rsa_pk()

        print(f"\n"+"#"*5 + "   examination AWS tokens starts   " + "#"*5)
        scan.scan_for_aws_key()

        pass

    def output(self):   
        pass


if __name__ == "__main__":
    img_name = str(sys.argv[1])
    #img_name = 'my_new_img'
    start_time = timeit.default_timer()
    print(start_time)
    analysing = AnalManager(img_name)
    print(f"#" * 5 + "   Preparing environment   " + "#" * 5 + "\n")
   # analysing.prepare_environment()
    print(f"#" * 5 + "   Preprocessing Image " +img_name + "   "+ "#" * 5 + "\n")
    analysing.preprocess()

    if analysing.necessary:
         print(f"#"*5 + "   " + img_name + "   Has to be analysed " + "#"*5 + "\n")
         print(f"#"*5 + "   Mounting   " + "#"*5 + "\n")
         analysing.mount()
         analysing.examine_deeply()
    end_time = timeit.default_timer()
    print(end_time-start_time)

