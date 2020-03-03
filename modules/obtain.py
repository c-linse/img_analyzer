import docker


class ImgObtain:

    def __init__(self, img_name):
        #   initialize environment
        self.client = docker.from_env()
        self.img_name = img_name

    #   stop possible running containers images
    def stop_all_containers(self):
        for container in self.client.containers.list():
            container.reload()
            container.stop()

    #   remove old images
    def remove_old_images(self):
        for img in self.client.images.list():
            self.client.images.remove(str(img.id), force=True)

    #   pull image
    def pull_image(self):
        if ':' in self.img_name:
            self.client.images.pull(self.img_name)
        else:
            self.client.images.pull(self.img_name + ':latest')
