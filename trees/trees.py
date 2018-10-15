import csv
from math import pi, sqrt, sin, cos, atan2

PATH_TO_DATESET = 'datasets/trees-census.csv'
EARTH_RADIUS_FT = 20888000
LAT_THRESHOLD = 0.00137150
RADIUS_FT = 500

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

tree_points_sorted = sorted(tree_points, key = lambda row: row['lat'])
max_neighbors = 0
max_points = []

test = tree_points_sorted

for idx, p1 in enumerate(test):
    print(f'>>>>>{idx}')
    neighboors = 0
    right = left = idx
    while right < len(test) and abs(p1['lat'] - test[right]['lat']) <= LAT_THRESHOLD:
        right += 1
    while left > 0 and abs(p1['lat'] - test[left]['lat']) <= LAT_THRESHOLD:
        left -= 1

    if (right - left) >= max_neighbors:

        for p2 in test[left:right+1]:
            if p1['id'] == p2['id']:
                continue

            if haversine(p1, p2) < RADIUS_FT:
                neighboors += 1

        if neighboors > 0:
            if neighboors > max_neighbors:
                print(f'new max neightbors: {neighboors}! (completion: {idx / len(test) * 100}%)')
                max_points = [p1]
                max_neighbors = neighboors
            elif neighboors == max_neighbors:
                print(f'max neightbors matched at {neighboors}! (completion: {idx / len(test) * 100}%)')
                max_points.append(p1)

print(max_neighbors)
print(max_points)

"""
Result:
"""
