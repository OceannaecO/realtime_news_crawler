import oss2
from ... import settings

class AliyunOss:
    def __init__(self):
        self.host = settings.OSS_HOST
        _auth = oss2.Auth(access_key_id=settings.ACCESS_KEY_ID,
                          access_key_secret=settings.ACCESS_KEY_SECRET)
        _bucket = settings.OSS_BUCKET
        self.bucket = oss2.Bucket(_auth, 'oss-cn-beijing.aliyuncs.com', _bucket)

    def upload_image(self, fullpath, objectname):
        self.upload_file(fullpath, objectname)
        return "{}/{}".format(self.host, objectname)

    def upload_file(self, fullpath, objectname):
        with open(fullpath, 'rb') as f:
            self.bucket.put_object(objectname, f)
