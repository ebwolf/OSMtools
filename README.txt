OSMtools

Python libraries for working with OpenStreetMap data.

Based on 

  Python OsmApi: http://wiki.openstreetmap.org/wiki/PythonOsmApi
  
  imposm: http://dev.omniscale.net/imposm.parser/
  
The goal is to provide a lightweight method of pulling data form the OSM API 
or planet files without imposing the OSM tagging schema.

There are two Python modules in OSMtools:

osmplanet.py

  Originally a version on imposm mod'd to read the Full Planet file.

  Reads OSM planet files in .osm (XML), .bz2 or .gz format.
  If it's .bz2, it can't have been compresed with pbzip2. 
  If it was, you have to convert it first:
  
  bzip2 -cd full-planet-110115-1800.osm.bz2 | bzip2 -c > full-planet.new.osm.bz2
  
  It understands the basic OSM XML schema and feeds individual 
  objects (nodes, ways, relations) to the DOM in order to produce
  a Python object that looks identical to what OsmAPI makes.
  
osmapi

  Largely identical to Ettiene Chove's osmapi. 
  
  One important "kludge":
  
    A "xapi" method is added which let's you pass an unchecked
    xapi query to the server. 
    
  I haven't used this in a while, so it may be broken.
  
  
