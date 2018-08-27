from main import logger

DOWNLOAD_BASE = 'https://dl.opensubtitles.org/en/download/sub/'

def download(url, download_id):
    output_dir = './Desktop/'
    zip_name = 'Subtitles'
    zip_path = output_dir + zip_name

    # Download zip
    import requests
    download_link = DOWNLOAD_BASE + download_id
    response = requests.get(download_link, headers={'referer': url})
    open(zip_path, 'wb').write(response.content)

    # Find the name of the '.srt' files inside the zip
    from zipfile import ZipFile
    zip_ref = ZipFile(zip_path, 'r')
    item_list = zip_ref.infolist()

    srt_list = []
    for item in item_list:
        logger.info('Checking zip file item: %s' % item.filename)
        if item.filename.endswith('.srt'):
            logger.info('%s is an srt file' % item.filename)
            srt_list.append(item)

    # Unzip only '.srt' files
    for srt in srt_list:
        zip_ref.extract(srt, output_dir)

    # Close zip
    zip_ref.close()
    
    # Delete zip
    import os
    os.remove(output_dir + zip_name)