# pylint: disable=E1101

import os
import arcpy
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

def node_generator(gtfs_folder):

    print('Building file geodatabase')
    gdb_folder = os.path.join(os.path.expanduser('~'),"OneDrive","Documents","ArcGIS","Projects","MBTA_Overview","GTFS","GTFS_gdb")
    gdb_path = os.path.join(gdb_folder,f"MBTA_GTFS_{date}.gdb")
    if arcpy.Exists(gdb_path):
        arcpy.Delete_management(gdb_path)
    gdb = arcpy.management.CreateFileGDB(gdb_folder, f"MBTA_GTFS_{date}")
    fd = arcpy.CreateFeatureDataset_management(gdb,"transit_network",'102100')
    path = arcpy.Describe(fd).catalogPath

    print('Building network nodes')
    arcpy.conversion.GTFSToNetworkDatasetTransitSources(gtfs_folder,fd,'INTERPOLATE')

    return path

def build_nd(template,gtfs_fd):
    nd = arcpy.na.CreateNetworkDatasetFromTemplate(template,gtfs_fd)

    # TODO: get network to build itself.
    #network = arcpy.na.BuildNetwork(nd)
    network = "This is a placeholder"
    return network

def main():

    # Extract GTFS data and save to a folder.
    gtfs_source = 'https://cdn.mbta.com/MBTA_GTFS.zip'
    gtfs_folder = gtfs_retriever(gtfs_source)
    # Clean GTFS data for consumption in GIS.
    gtfs_cleaner(gtfs_folder)
    # Build nodes and paths from GTFS data. Returns feature dataset with datapoints for network.
    gtfs_fd = node_generator(gtfs_folder)

    # TODO: Add code to pull and prep streets from MassDOT Road Inventory. This section will be converted to a module.
    streets_source = os.path.join(os.path.expanduser('~'),"OneDrive","Documents","ArcGIS","Projects","MBTA_Overview","MBTA_Overview.gdb","streets")
    streets = arcpy.conversion.FeatureClassToFeatureClass(streets_source,gtfs_fd,"streets")

    # Connect to streets. Some warnings are expected. Will handle these in the future, but usually requires some manual cleanup.
    arcpy.conversion.ConnectNetworkDatasetTransitSourcesToStreets(gtfs_fd, streets, "100 Meters", "RestrictPedestrians <> 'Y'")

    template = os.path.join(os.path.expanduser('~'),"OneDrive","Documents","ArcGIS","Projects","MBTA_Overview","GTFS","TransitNetworkTemplate.xml")
    network = build_nd(template,gtfs_fd)

    print("Complete")


main()