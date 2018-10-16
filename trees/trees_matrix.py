"""
This algorithm uses a divide and conquer strategy by using a matrix.

It creates square zones that have a side 4 times the radius. The zones overlap
each other half-way through. This creates some redundancy to handle cases of
trees being on the outside part of the zone that is closer than RADIUS_FT to
the edge.

We then further speed up the processing by sorting each point in a zone by
longitude. This allows us to only select only the points that are withing
RADIUS_FT of each other before looking for neighboors.

If we were to find neighboors on the whole, undivided dataset, the time
complexity would be N^2. Because we are dividing the points into zones append
then further selecting only points with RADIUS_FT we are able to bring the
algorithm runtime to about N LOG N.
"""

import csv
from math import pi, sqrt, sin, cos, atan2

PATH_TO_DATESET = 'datasets/trees-census.csv'
EARTH_RADIUS_FT = 20888000
FT_DEGREES = 0.00000275
RADIUS_FT = 500
LONG_THRESHOLD = RADIUS_FT * FT_DEGREES
ZONE_D = RADIUS_FT * 4 * FT_DEGREES # length of a side of a square zone

def haversine(pos1, pos2):
    """ Returns distande between 2 coordinates in feet
    """
    lat1 = float(pos1['lat'])
    long1 = float(pos1['long'])
    lat2 = float(pos2['lat'])
    long2 = float(pos2['long'])

    degree_to_rad = float(pi / 180.0)

    d_lat = (lat2 - lat1) * degree_to_rad
    d_long = (long2 - long1) * degree_to_rad

    a = pow(sin(d_lat / 2), 2) + cos(lat1 * degree_to_rad) * cos(lat2 * degree_to_rad) * pow(sin(d_long / 2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    feet = EARTH_RADIUS_FT * c

    return feet

tree_points = []

with open(PATH_TO_DATESET) as csvfile:
    treereader = csv.reader(csvfile)
    next(treereader, None)  # skip the headers
    for row in treereader:
        tree_points.append({'id': row[1], 'lat': float(row[38]), 'long': float(row[39])})

sorted_lat = sorted(tree_points, key = lambda row: row['lat'])
sorted_long = sorted(tree_points, key = lambda row: row['long'])

bottom_lat = sorted_lat[0]['lat'] - ZONE_D # bottom
top_lat = sorted_lat[len(tree_points) - 1]['lat'] + ZONE_D # top
left_long = sorted_long[0]['long'] - ZONE_D # left
right_long = sorted_long[len(tree_points) - 1]['long'] + ZONE_D # right

print(f"""
    bottom_lat: {bottom_lat}
    top_lat = : {top_lat}
    left_long : {left_long}
    right_long: {right_long}

""")
# testing
# bottom_lat = 40.49846614 # bottom
# top_lat = 40.91291831 # top
# left_long = -74.24130162 # left
# right_long = -73.90234893 # right

width = top_lat - bottom_lat
height = abs(right_long - left_long)


class Matrix():
    def __init__(self, bottom_lat, top_lat, left_long, right_long):
        curr_lat = top_lat
        self.matrix = []

        while curr_lat > bottom_lat:
            curr_lat_zones = LatZones(curr_lat - ZONE_D, curr_lat)
            curr_long = left_long
            while curr_long < right_long:
                zone = Zone(curr_lat - ZONE_D, curr_lat, curr_long, curr_long + ZONE_D)
                curr_lat_zones.zones.append(zone)
                curr_long += ZONE_D / 2

            self.matrix.append(curr_lat_zones)
            curr_lat -= ZONE_D / 2

    def __repr__(self):
        return f"""
            Height = {len(self.matrix)}
            Width = {len(self.matrix[0].zones)}
        """

    def distribute_points(self, sorted_long_points):
        matrix = self.matrix

        print(f'Distributing {len(sorted_long_points)} points...')
        for point in sorted_long_points:

            i = 0
            while point['lat'] > matrix[i].top_lat or point['lat'] < matrix[i].bottom_lat:
                i += 1

            j = 0
            zones = matrix[i].zones
            while point['long'] < zones[j].left_long or point['long'] > zones[j].right_long:
                j += 1

            zones[i].points.append(point)

        print('Distribution DONE')

    def find_most_neighbors(self):
        max_neighbors = 0
        max_points = []

        for idx1, lat_zone in enumerate(matrix.matrix):
            for idx2, zone in enumerate(lat_zone.zones):
                points = zone.points
                print(f"""
                    LatZones: {idx1}
                    Zone: {idx2}
                    Point Count: {len(points)}
                """)
                for idx3, p1 in enumerate(points):
                    points_len = len(points)
                    neighboors = 0
                    right = left = idx3

                    while right < points_len and abs(p1['long'] - points[right]['long']) <= LONG_THRESHOLD:
                        right += 1
                    while left > 0 and abs(p1['lat'] - points[left]['long']) <= LONG_THRESHOLD:
                        left -= 1

                    selected_points = right - left

                    if selected_points >= max_neighbors:

                        for p2 in points[left:right+1]:
                            if p1['id'] == p2['id']:
                                continue

                            if haversine(p1, p2) < RADIUS_FT:
                                neighboors += 1

                        if neighboors > 0:
                            if neighboors > max_neighbors:
                                max_points = [p1]
                                max_neighbors = neighboors
                            elif neighboors == max_neighbors:
                                max_points.append(p1)

        print(f"""
            Points: {max_points}
            Neighboors count: {max_neighbors}
        """)

class LatZones():
    def __init__(self, bottom_lat, top_lat):
        self.bottom_lat = bottom_lat
        self.top_lat = top_lat
        self.zones = []

    def __repr__(self):
        return f"""
            Top: {self.top_lat}
            Bottom: {self.bottom_lat}
        """


class Zone():
    def __init__(self, bottom_lat, top_lat, left_long, right_long):
        self.bottom_lat = bottom_lat
        self.top_lat = top_lat
        self.left_long = left_long
        self.right_long = right_long
        self.points = []

    def __repr__(self):
        return f"""
            {self.bottom_lat}
            {self.top_lat}
            {self.left_long}
            {self.right_long}
        """

if __name__ == "__main__":
    matrix = Matrix(bottom_lat, top_lat, left_long, right_long)
    matrix.distribute_points(sorted_long)
    matrix.find_most_neighbors()
