# pylint: disable=E1101

import os
from datetime import datetime

date = datetime.today().strftime('%Y%m%d')

def gtfs_retriever(gtfs_source):

    import requests
    from zipfile import ZipFile
    
    gtfs_zip = requests.get(gtfs_source)
    raw_path = os.path.join(os.path.expanduser('~'),"OneDrive","Documents","ArcGIS","Projects","MBTA_Overview","GTFS","GTFS_raw",f"{date}_GTFS")

    with open(f"{raw_path}.zip","wb") as zip:
        zip.write(gtfs_zip.content)

    with ZipFile(f"{raw_path}.zip",'r') as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall(raw_path)
        print('File is unzipped in temp folder')
    os.remove(f"{raw_path}.zip")

    return raw_path

def gtfs_cleaner(gtfs_folder):
    import pandas as pd

    df = pd.read_csv(gtfs_folder+'\\stops.txt')
    df = df.dropna(subset=['stop_lat', 'stop_lon'])
    df.to_csv(gtfs_folder+'\\stops.txt',index=False)


def nd_builder(gtfs_folder):
    import arcpy

    print('Building file geodatabase')
    gdb_folder = os.path.join(os.path.expanduser('~'),"OneDrive","Documents","ArcGIS","Projects","MBTA_Overview","GTFS","GTFS_gdb")
    gdb_path = os.path.join(gdb_folder,f"MBTA_GTFS_{date}.gdb")
    if arcpy.Exists(gdb_path):
        arcpy.Delete_management(gdb_path)
    gdb = arcpy.management.CreateFileGDB(gdb_folder, f"MBTA_GTFS_{date}")
    fd = arcpy.CreateFeatureDataset_management(gdb,"transit_network",'102100')

    print('Building network')
    arcpy.conversion.GTFSToNetworkDatasetTransitSources(gtfs_folder,fd,'INTERPOLATE')

def main():

    gtfs_source = 'https://cdn.mbta.com/MBTA_GTFS.zip'
    gtfs_folder = gtfs_retriever(gtfs_source)

    gtfs_cleaner(gtfs_folder)

    nd_builder(gtfs_folder)

    print("Complete")


main()