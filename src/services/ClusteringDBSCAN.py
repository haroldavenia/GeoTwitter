from sklearn.cluster import DBSCAN
from collections import Counter
import numpy as np


class ClusteringDBSCAN:
    def __init__(self):
        # Initialize the DBSCAN clustering algorithm with specific parameters
        self.dbscan = DBSCAN(eps=0.1077, min_samples=5)

    def centroid_most_dense(self, points):
        # Convert points into a NumPy array of (x, y) coordinates
        shapely_points = np.array([(point.get('x'), point.get('y')) for point in points])

        # Apply DBSCAN clustering to the points
        clusters = self.dbscan.fit_predict(shapely_points)

        # Count the number of points in each cluster
        cluster_counts = Counter(clusters)

        # Find the cluster with the highest density (excluding noise, labeled as -1)
        most_dense_cluster_label = max(cluster_counts, key=lambda x: cluster_counts[x] if x != -1 else 0)

        # Get the points from the most dense cluster
        most_dense_cluster_points = [points[idx] for idx, value in enumerate(clusters)
                                     if value == most_dense_cluster_label]

        return most_dense_cluster_points
