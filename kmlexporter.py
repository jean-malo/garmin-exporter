import argparse
import codecs
import csv
import json
import xml.etree.ElementTree as ET

def build_tree(path):
    tree = ET.parse(path)
    return tree


def fetch_waypoints(root):
    for i in root.findall(f'.//{schema}Placemark'):
        yield format_waypoint(i)


def format_waypoint(waypoint):
    date = waypoint.find(f'.//{schema}when')
    latitude = fetch_data(waypoint, "Latitude")
    longitude = fetch_data(waypoint, "Longitude")
    elevation = fetch_data(waypoint, "Elevation")
    velocity = fetch_data(waypoint, "Velocity")
    course = fetch_data(waypoint, "Course")
    valid_gps_fix = fetch_data(waypoint, "Valid GPS Fix")
    in_emergency = fetch_data(waypoint, "In Emergency")
    in_emergency = True if in_emergency in {"True", "true"} else False  # Garmin export not consistent
    event = fetch_data(waypoint, "Event")
    imei = fetch_data(waypoint, "IMEI")

    return {'date': date,
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation,
            'velocity': velocity,
            'course': course,
            'valid_gps_fix': valid_gps_fix,
            'in_emergency': in_emergency,
            'event': event,
            'imei': imei}


def fetch_data(root, target):
    data = root.find(f'.//{schema}Data[@name="{target}"]/{schema}value')
    return data.text if data is not None else None


def save_as_csv(root, path):
    fieldnames = ['date', 'latitude', 'longitude', 'elevation', 'velocity', 'course', 'valid_gps_fix', 'in_emergency',
                  'event', 'imei']
    with open(f"{path}.csv", "w") as file:
        writer = csv.DictWriter(file, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        for waypoint in fetch_waypoints(root):
            writer.writerow(waypoint)


def save_as_json(root, path):
    with codecs.open(f"{path}.json", "w", encoding="utf-8") as file:
        for waypoint in fetch_waypoints(root):
            json.dump(waypoint, file, ensure_ascii=False, default=str)  # Save dates as str in iso format


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description="Convert kml files provided by garmin in csv or json.")
    args_parser.add_argument("-i", "--input", type=str, help="The path to the kml file provided by garmin.",
                             required=True)
    args_parser.add_argument("-o", "--output", type=str, help="Where to save the ouput (include the filename).",
                             required=True, default="Garmin_export")
    args_parser.add_argument("-f", "--format", type=str, help="Format of export", required=False, default="csv",
                             choices=['csv', 'json'])
    args = args_parser.parse_args()
    tree = build_tree(args.input)
    schema = '{http://www.opengis.net/kml/2.2}'
    if args.format == 'csv':
        save_as_csv(tree, args.output)
    if args.format == 'json':
        save_as_json(tree, args.output)
