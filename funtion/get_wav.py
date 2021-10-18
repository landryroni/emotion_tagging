import os

# Get all .wav audio paths under the specified folder and its subfolders
def get_all_wav_paths(file_dir):
    '''
    获取指定文件夹及其子文件夹下的所有.wav音频路径
    需要导入的库：numpy,librosa
    :param file_dir: 文件夹地址（str）
    :return: 音频地址列表（list）
    '''
    _wav_paths = []
    for dir, sub_dir, file_base_name in os.walk(file_dir):
        for file in file_base_name:
            if file.endswith(".wav") or file.endswith(".WAV"):
                _wav_paths.append(os.path.join(dir, file))
    return _wav_paths
