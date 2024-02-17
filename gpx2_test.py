import csv
import xml.etree.ElementTree as ET
from geopy.distance import geodesic
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

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
            interval_data['pace'] = extract_avg_speed(interval_data['total_time'], interval_data['distance'])
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
            interval_data['pace'] = extract_avg_speed(interval_data['total_time'], interval_data['distance'])
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
    
def extract_avg_speed(time, dist): 

    dist /= 1000
    avg_pace = time / dist

    if avg_pace is not None:
        return convert_time(avg_pace)
    else: 
        return 0
    
def convert_time(time):
    time_minutes = time // 60
    time_sec = time % 60

    return(f"{int(time_minutes):02}'{int(time_sec):02}")

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("GPX files", "*.gpx")])
    return file_path

    
def write_intervals_csv(intervals, csv_file):
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Interval' , 'Action', 'Start Time', 'End Time', 'Total Time (s)', 'Distance (m)', 'Max Heart Rate (bpm)', 'Pace(min/km)'])
        writer.writeheader()
        for i, interval in enumerate(intervals, start=1):
            writer.writerow({'Interval': i,
                             'Action': interval['action'],
                             'Start Time': interval['start_time'],
                             'End Time': interval['end_time'],
                             'Total Time (s)': convert_time(interval['total_time']),
                             'Distance (m)': interval['distance'],
                             'Max Heart Rate (bpm)': interval['max_heart_rate'],
                             'Pace(min/km)' : interval['pace']})

if __name__ == "__main__":
    gpx_file = select_file()
    csv_file = input("Enter output filename: ") + ".csv"
    warmup_distance_treshold = input("Enter warm-up distance in Meters: ")
    interval_distance_threshold = input("Enter training distance in Meters: ")
    intervals = extract_intervals(gpx_file, interval_distance_threshold)
    write_intervals_csv(intervals, csv_file)
    print(f"Interval data extracted and saved to {csv_file}")
