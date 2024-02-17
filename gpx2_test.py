import csv
import xml.etree.ElementTree as ET
from geopy.distance import geodesic
from datetime import datetime

def extract_intervals(gpx_file, interval_distance_threshold):
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    # Extract track points
    track_points = []
    for track in root.findall('.//{http://www.topografix.com/GPX/1/1}trk'):
        for segment in track.findall('{http://www.topografix.com/GPX/1/1}trkseg'):
            for point in segment.findall('{http://www.topografix.com/GPX/1/1}trkpt'):
                track_points.append(point)

    # Extract intervals based on distance threshold
    intervals = []
    interval_count = 1
    interval_start_point = None
    total_distance = 0
    #warmup_distance = 1
    for i in range(1, len(track_points)):
        point1 = track_points[i - 1]
        point2 = track_points[i]
        coords1 = (float(point1.get('lat')), float(point1.get('lon')))
        coords2 = (float(point2.get('lat')), float(point2.get('lon')))
        distance = geodesic(coords1, coords2).meters
        total_distance += distance
        if interval_start_point is None:
            interval_start_point = point1

        elif total_distance >= int(warmup_distance_treshold) and interval_count == 1:
            interval_data = {}
            interval_data['action'] = 'Warm-up'
            interval_data['start_time'] = interval_start_point.find('{http://www.topografix.com/GPX/1/1}time').text
            interval_data['end_time'] = point2.find('{http://www.topografix.com/GPX/1/1}time').text
            interval_data['total_time'] = (datetime.strptime(interval_data['end_time'], '%Y-%m-%dT%H:%M:%SZ') -
                                            datetime.strptime(interval_data['start_time'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
            interval_data['distance'] = round(total_distance, 0)
            interval_data['max_heart_rate'] = extract_max_heart_rate(point2)
            interval_data['avg_speed'] = extract_avg_speed(point1)
            intervals.append(interval_data)
            total_distance = 0
            interval_count += 1
            interval_start_point = None
             
        elif total_distance >= int(interval_distance_threshold):
            interval_data = {}
            if interval_count % 2 == 0:
              interval_data['action'] = 'Training'
            else:
              interval_data['action'] = 'Break'  
            interval_data['start_time'] = interval_start_point.find('{http://www.topografix.com/GPX/1/1}time').text
            interval_data['end_time'] = point2.find('{http://www.topografix.com/GPX/1/1}time').text
            interval_data['total_time'] = (datetime.strptime(interval_data['end_time'], '%Y-%m-%dT%H:%M:%SZ') -
                                            datetime.strptime(interval_data['start_time'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds()
            interval_data['distance'] = round(total_distance, 0)
            interval_data['max_heart_rate'] = extract_max_heart_rate(point2)
            interval_data['avg_speed'] = extract_avg_speed(point2)
            intervals.append(interval_data)
            total_distance = 0
            interval_count += 1
            interval_start_point = None

    return intervals

def extract_max_heart_rate(point):
    heart_rate = point.find('{http://www.topografix.com/GPX/1/1}extensions/{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension/'
                            '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr')
    if heart_rate is not None:
        return int(heart_rate.text)
    else:
        return 0  # If heart rate data is not available, return 0 or any other default value
    
def extract_avg_speed(spd):
    avg_speed = spd.find('{http://www.topografix.com/GPX/1/1}extensions/{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension/'
                         '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}speed')
    
    if avg_speed is not None:
        return float(avg_speed.text)
    else: 
        return 0
    
def convert_time(time):
    time_minutes = time // 60
    time_sec = time % 60

    return(f"{int(time_minutes):02}'{int(time_sec):02}")
    
def write_intervals_csv(intervals, csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Interval' , 'Action', 'Start Time', 'End Time', 'Total Time (s)', 'Distance (m)', 'Max Heart Rate (bpm)', 'Pace'])
        writer.writeheader()
        for i, interval in enumerate(intervals, start=1):
            writer.writerow({'Interval': i,
                             'Action': interval['action'],
                             'Start Time': interval['start_time'],
                             'End Time': interval['end_time'],
                             'Total Time (s)': convert_time(interval['total_time']),
                             'Distance (m)': interval['distance'],
                             'Max Heart Rate (bpm)': interval['max_heart_rate'],
                             'Pace' : interval['avg_speed']})

if __name__ == "__main__":
    gpx_file = 'input.gpx'
    csv_file = 'interval_data.csv'
    warmup_distance_treshold = input("Enter warm-up distance in Meters: ")
    interval_distance_threshold = input("Enter training distance in Meters: ")
    #warmup_distance_treshold = 340 # Example threshold 340 meter
    #interval_distance_threshold = 400  # Example threshold: 1000 meters
    intervals = extract_intervals(gpx_file, interval_distance_threshold)
    write_intervals_csv(intervals, csv_file)
    print(f"Interval data extracted and saved to {csv_file}")
