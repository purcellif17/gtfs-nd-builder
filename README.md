# gtfs-nd-builder
Builds a geospatial network dataset from current MBTA GTFS data.

At the moment, this script downloads the GTFS data and runs it through the ArcGIS tool to create a usable network. Future improvements include downloading street data, and actuallyg generating a network dataset.

This code is based on the workflow of the [Create and use a network dataset with public transit data](https://pro.arcgis.com/en/pro-app/latest/help/analysis/networks/create-and-use-a-network-dataset-with-public-transit-data.htm) tutorial for ArcGIS Pro. The TransitnetworkTemplate.xml document comes straight from that tutorial and I take no credit for it.