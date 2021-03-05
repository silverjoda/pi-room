import os, shutil
folders = ['audio', 'logs', 'analysis', 'raw_images', 'npz_images']
for f in folders:
    if not os.path.exists(f): continue
    for filename in os.listdir(f):
        file_path = os.path.join(f, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))