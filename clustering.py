import matplotlib.pyplot as pyplot
import numpy
import python_speech_features
import sklearn.cluster
import shutil
import soundfile
from pathlib import Path
from scipy import signal

class Sound:
    def __init__(self, path):
        self.path = path

        path_str = str(path)
        self.data, self.samplerate = soundfile.read(path_str)
        self.rule = self.get_rule_from_file_name(path_str)

        # self.extract_spectrogram()
        self.extract_mfcc()

    def get_rule_from_file_name(self, path_str):
        # Format 1-2-3-P4-5_foo_bar.wav into 1/2/3:P4,5
        rule = path_str.split("/")[1].split("_")[0].split("P")
        rule[0] = rule[0].replace("-", "/", 2).replace("-", ":")
        rule[1] = rule[1].replace("-", ",")
        return "P".join(rule)

    def extract_spectrogram(self, n_frame=39):
        self.frequency, self.time, self.spectrogram = signal.spectrogram(
            self.data, self.samplerate)
        if self.spectrogram.shape[1] < n_frame:
            zeros = numpy.zeros((self.spectrogram.shape[0],
                                 n_frame - self.spectrogram.shape[1]))
            self.spectrogram = numpy.concatenate((self.spectrogram, zeros), axis=1)
        elif self.spectrogram.shape[1] > n_frame:
            self.spectrogram = self.spectrogram[:][0:n_frame]
        self.raveled_spectrogram = numpy.ravel(self.spectrogram)

    def extract_mfcc(self, n_frame=19):
        self.mfcc = python_speech_features.mfcc(
            self.data, self.samplerate, winlen=0.0116)
        if self.mfcc.shape[0] < n_frame:
            zeros = numpy.zeros((n_frame - self.mfcc.shape[0], self.mfcc.shape[1]))
            self.mfcc = numpy.concatenate((self.mfcc, zeros), axis=0)
        elif self.mfcc.shape[0] > n_frame:
            self.mfcc = self.mfcc[0:n_frame]
        self.raveled_mfcc = numpy.ravel(self.mfcc)

def create_sound_list(directory):
    # 事前にwavの長さを一定にそろえておく。
    return [
        Sound(wav_path)
        for index, wav_path in enumerate(Path(directory).glob("*.wav"))
    ]

def gather_points(sounds):
    return numpy.array([sound.raveled_mfcc for sound in sounds])
    # return numpy.array([sound.raveled_spectrogram for sound in sounds])

def mkdir_for_output(n_clusters, method_name):
    output_directories = [
        Path("cluster/" + method_name + "_" + data_directory + f"/set{i:02d}")
        for i in range(n_clusters)
    ]

    for out_dir in output_directories:
        out_dir.mkdir(parents=True, exist_ok=True)

    return output_directories

def write_result(method_name, n_clusters, labels, sounds):
    output_directories = mkdir_for_output(n_clusters, method_name)
    for label, sound in zip(labels, sounds):
        shutil.copy(sound.path, output_directories[label])

def create_kmeans_cluster(sounds, points, n_clusters):
    cluster = sklearn.cluster.KMeans(
        n_clusters=n_clusters, random_state=0).fit(points)
    write_result("kmeans", n_clusters, cluster.labels_, sounds)

def create_affinity_propagation_cluster(sounds, points):
    cluster = sklearn.cluster.AffinityPropagation(damping=0.6, max_iter=2**10).fit(points)
    print(cluster.n_iter_)
    write_result("affinity_propagation", len(cluster.cluster_centers_),
                 cluster.labels_, sounds)

def create_agglomerative_cluster(sounds, points, n_clusters):
    cluster = sklearn.cluster.AgglomerativeClustering(
        n_clusters=n_clusters).fit(points)
    write_result("agglomerative", n_clusters, cluster.labels_, sounds)

def create_spectral_cluster(sounds, points, n_clusters):
    cluster = sklearn.cluster.SpectralClustering(
        n_clusters=n_clusters).fit(points)
    write_result("spectral", n_clusters, cluster.labels_, sounds)

data_directory = "snd"
sounds = create_sound_list(data_directory)
points = gather_points(sounds)

n_clusters = 12
create_kmeans_cluster(sounds, points, n_clusters)
create_affinity_propagation_cluster(sounds, points)
create_agglomerative_cluster(sounds, points, n_clusters)
create_spectral_cluster(sounds, points, n_clusters)
"""
TODO:
# 評価。
# 特徴の正規化。

DONE:
# 他のクラスタリングを試す。

次のクラスタリングを試した。

- KMeans
- AffinityPropagation
- AgglomerativeClustering
- SpectralClustering
- DBSCAN

KMeansで十分にいい。
AgglomerativeもKMeansと似たような感じ。
AffinityPropagationはパラメータの設定が異なる。damping を 0.5 にするとクラスタの数が多くなりすぎる。適当に0.6としたところ119のサンプルに対して60ほどあったクラスタが15まで減った。
SpectralClusteringは良くない。
DBSCANは使い方がわからなかった。

# 特徴を変える。
`scipy.signal.spectrogram` から `python_speech_features.mfcc` に変えたところ結果が改善した。

# DBSCANの使い方を調べる
DBSCANは空間を格子に区切って、格子内のデータポイントの密度に応じてクラスタを作る。
今回のデータでは次元の高さに対してデータポイントの数が少なすぎてDBSCANは使えなさそう。

- [Visualizing DBSCAN Clustering](https://www.naftaliharris.com/blog/visualizing-dbscan-clustering/)
"""
