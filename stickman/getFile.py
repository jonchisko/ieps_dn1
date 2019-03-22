import urllib.request
import os

#tries to retrieve the file
#if it fails we just say that the picture doesn't exist
class GetFileFromURL:

    @staticmethod
    def get_file_from_url(url):
        file_name = url.split("/")[-1]
        file_type = file_name.split(".")[-1]
        try:
            urllib.request.urlretrieve(url, file_name)
            return file_name, file_type
        except:
            return False

    @staticmethod
    def delete_file_from_disc(file_name):
        try:
            os.remove(file_name)
        except:
            return

if __name__ == "__main__":
    a,b = GetFileFromURL.get_file_from_url("http://www.e-prostor.gov.si/fileadmin/_processed_/b/b/csm_eProstor_logotip_253px_c037bbc40d.png")

    print(GetFileFromURL.get_file_from_url("http://evem.gov.si/evem_static/images/YEURO.png"))
    GetFileFromURL.delete_file_from_disc(a)
