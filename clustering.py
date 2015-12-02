# -*- coding: utf-8 -*-

import sys
import os
import codecs
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster                 import KMeans, MiniBatchKMeans
from sklearn.decomposition           import TruncatedSVD
from sklearn.preprocessing           import Normalizer

class Analyzer:
  def __init__(self, args):
    self.infile       = args[1]
    self.outfile      = args[2]
    self.num_clusters = 5       # クラス数
    self.max_df       = 0.8     # ベクトル生成に必要な値
    self.max_features = 10000   # ベクトル生成に必要な値
    self.minibatch    = True    # 条件判定

  # テキストを読込
  def _read_from_file(self):
    list = []
    file = open(self.infile, 'r')
    for line in file:
      list.append( line.rstrip() )
    file.close
    return list

  # クラスタを作成
  def make_cluster(self):
    texts = self._read_from_file()
    # print "texts are %(texts)s" %locals()

    # ベクトルを生成
    vectorizer = TfidfVectorizer(
      max_df       = self.max_df,
      max_features = self.max_features,
      stop_words   = 'english'
      )
    X = vectorizer.fit_transform(texts)
    # ここでの値は何度やっても同じでした
    # print "X values are %(X)s" %locals()

    # KMeans インスタンスを生成しクラスタリングする
    # パラメータはデータの量や特性に応じて適切なものを与えるようにする
    if self.minibatch:
      km = MiniBatchKMeans(
        n_clusters         = self.num_clusters,
        init               = 'k-means++',
        batch_size         = 1000,
        n_init             = 10,
        max_no_improvement = 10,
        verbose            = True
        )
    else:
      km = KMeans(
        n_clusters = self.num_clusters,
        init       = 'k-means++',
        n_init     = 1,
        verbose    = True
        )
    km.fit(X)
    labels = km.labels_

    transformed = km.transform(X)
    dists       = np.zeros(labels.shape)
    for i in range(len(labels)):
      dists[i] = transformed[i, labels[i]]

    clusters = []
    for i in range(self.num_clusters):
      cluster = []
      ii      = np.where(labels==i)[0]
      dd      = dists[ii]
      di      = np.vstack([dd,ii]).transpose().tolist()
      di.sort()
      for d, j in di:
        cluster.append(texts[int(j)])
      clusters.append(cluster)

    return clusters

  def write_cluster(self, clusters):
    f = codecs.open('%s' % self.outfile, 'w', 'utf-8')
    for i, texts in enumerate(clusters):
      for text in texts:
        f.write('%d: %s\n' % (i, text.replace('/n', '').decode('utf-8')))

if __name__ == '__main__':
  if len(sys.argv) > 2:
    analyzer = Analyzer(sys.argv)
    clusters = analyzer.make_cluster()
    # print "Result clusters are %(clusters)s" %locals()
    analyzer.write_cluster(clusters)
  else:
    print "Invalid arguments"
