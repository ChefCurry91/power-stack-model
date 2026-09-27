#import matplotlib.pyplot as plt

#plt.figure(figsize=(10, 8))

#plt.scatter( 
 #   coordinates_solar_capacities["x_coordinates"],
#    coordinates_solar_capacities["y_coordinates"],
#    c=coordinates_solar_capacities["cluster"],
#    s=5,
#    alpha=0.6
#)

#plt.xlabel("Longitude")
#plt.ylabel("Latitude")
#plt.title("Solar installations by geographic cluster")

#plt.scatter(
#    kmeans.cluster_centers_[:, 0],  # x des centres
#    kmeans.cluster_centers_[:, 1],  # y des centres
#    c="red", marker="x", s=100, label="Centroids"
#)
#plt.legend()

#plt.show()