#! /usr/bin/python
#
#  USGS Preliminary Computer Program: OsmPlanet.py
#  Written by: Eric B. Wolf
#  Written in: Python 2.7.1
#  Program ran on: Windows XP SP3
#
#  DISCLAIMER: Although this program has been used by the USGS, no warranty, 
#  expressed or implied, is made by the USGS or the United States Government 
#  as to the accuracy and functioning of the program and related program 
#  material nor shall the fact of distribution constitute any such warranty, 
#  and no responsibility is assumed by the USGS in connection therewith.
#
import bz2, gzip
import os
import xml.dom.minidom

# OsmPlanet
#
# Automatically handles straight text osm, as well as bz2, gz compressed files
#
# Does not decompress the file if its compressed
# Does not care about end of line markers.
# Does not quite handle Unicode properly. But that may be an artifact of
#  the .OSM files I got from CloudMade
#
# Reads one XML object at a time and feeds it to the DOM parser. The resulting
# data looks and feels just like OsmApi.
#
# As of Python 2.7.1, it cannot read multi-stream BZ2 files made by pbzip2
# Except for that... it works with full-planet.osm
#
###########################################################################
## Main class                                                            ##

class OsmPlanet:
    
    def __init__(self, 
                 filename = None):
        
        self.name = filename

        self.root = ""
        self.ext = ""
        (self.root, self.ext) = os.path.splitext(filename.lower())
        
        try:
            # Automatically handle bz2/gz and plain osm/xml as input files
            if self.ext == '.bz2':
                self.fp = bz2.BZ2File(filename,'r')
            elif self.ext == '.gz':
                self.fp = gzip.open(filename,'r')
            else: # self.ext == '.osm':
                self.fp = open(filename, mode='rt')
        except:
            print "Error opening " + filename + "."
            exit(-1)
            
            
        # Prepare a buffer of data from the file.
        self.buffer_size = 16*1024*1024 # How many bytes to keep around in the buffer
        self.buffer_pos = 0
        self.buffer = self.fp.read(self.buffer_size)
        self.bytes_read = len(self.buffer)
        self.buffer_count = 0
        self.line_count = 0

        self.xml_version = '1.0'
        self.xml_encoding = 'UTF-8'
        self.osm_version = '0.6'
        self.osm_generator = ''
        self.bound_box = ''
        
        self.getDeclarations()
        
    def __del__(self):
        self.fp.close()
        return None        

    def findUnquoted(self, f):
        # Return the position of the 'f' not in quotes.
        sf = self.buffer_pos
        
        pf = self.buffer[sf:].find(f)
 
        if pf < 0:
            return pf
        
        qc = self.buffer[sf:sf + pf].count('"')
 
        # Even number of quotes before our character
        if not qc % 2:
            return sf + pf
            
        # Odd number of quotes is a special (rare) case
        while True: 
            sf = sf + pf + 1
            
            # Find the next 
            pf = self.buffer[sf:].find(f)
 
            if pf < 0:
                return pf
            
            # How many quotes are there before our character?
            qc += self.buffer[sf:sf + pf].count('"')
            
            if not qc % 2:
                return sf + pf
            
            # Hit the end of the buffer
            if sf + pf > len(self.buffer):
                return -1
            
        return -1
    
        
    def getNextTag(self):
        # find the close bracket
        cb = self.findUnquoted('>')
        
        # Hit the end of the buffer, need to reload
        if cb < 0:

            # Read in anohter chunk of the file
            # NOTE: It's possible that an XML tag will be greater than buffsize
            #       This will break in that situation.
            newb = self.fp.read(self.buffer_size)
            
            # Hit the end of the file, need to return zero-length
            if len(newb) == 0:
                return ''

            self.buffer_count += 1
            
            self.bytes_read = self.bytes_read + len(newb)
            
            # Copy the end of the buffer to head, tack on the new stuff
            self.buffer = self.buffer[self.buffer_pos:]+newb
            
            self.buffer_pos = 0
            
            # Check again for the close bracket
            cb = self.findUnquoted('>')
            
            if cb < 0:
                return ''

        # Pick out the tag and clean it up                
        tag = self.buffer[self.buffer_pos:cb+1]
        tag = tag.strip()
        
        if not isinstance(tag, unicode):
            tag = unicode(tag, self.xml_encoding, "ignore")

        # shift our buffer pointer up        
        self.buffer_pos = cb + 1

        # Very rare - happens if '>' is last character in buffer
        if self.buffer_pos >= len(self.buffer):
            newb = self.fp.read(self.buffer_size)
            self.buffer = newb
            self.buffer_count += 1
            self.bytes_read += len(newb)
            self.buffer_pos = 0

        self.line_count += 1
            
        return tag
      

    #---------------------------------------------------------------------------
    # Reads the XML declarations - version, encoding, etc.
    #---------------------------------------------------------------------------
    def getDeclarations(self):
        while True:
            # Save the buffer position so we can rewind
            bp = self.buffer_pos
            
            line = self.getNextTag()
            
            # Hit end of file? That's odd but not necessarily a failure.
            if line == '':
                break

            element = line[1:line.find(' ', 1)]
                
            if element == '?xml':
                # XML tag may have single or double quotes
                q = '"'
                t = line.find(q)
                if t < 0:
                    q = "'"
                    
                s = line.find('version=' + q, 4) + 9
                if s > 0:
                    e = line.find(q, s)
                    self.xml_version = line[s:e]
                
                s = line.find('encoding=' + q, 4) + 10
                if s > 0:
                    e = line.find(q, s)
                    self.xml_encoding = line[s:e]
                    
            elif element == 'osm':
                s = line.find('version="', 4) + 9
                if s > 0:
                    e = line.find('"', s)
                    self.osm_version = line[s:e]
                    
                s = line.find('generator="', 4) + 11
                if s > 0:
                    e = line.find('"', s)
                    self.osm_generator = line[s:e]
                
            elif element == 'bound':
                s = line.find('box="', 4) + 5
                if s > 0:
                    e = line.find('"', s)
                    self.bound_box = line[s:e]
            else:
                # Must be in the real elements - rewind the buffer position and get out of here
                self.buffer_pos = bp
                break
            
        # while(true):
        
        return

    # --- End: getPreamble
        

    #---------------------------------------------------------------------------
    # Parses the entire next object for high-level work
    #---------------------------------------------------------------------------
    def getNextObject(self):
        data = ''
        etype = ''
        
        while True:
            line = self.getNextTag()
            
            if line == '':
                break

            # End of file - we're done here!
            if line[1:5] == '/osm':
                break

            # Last line of element - append and go!
            if line[1] == '/':
                data += line
                break

            # Get the element type
            element = line[1:line.find(' ', 1)]

            if element in ('node', 'way', 'relation', 'changeset'):
                etype = element

                # Single line element - grab and go!
                if line[-2] == '/':
                    data = line
                    break
                
                
            data += line
            
        # While true  

        if data != '':
            data = data.encode("utf8")
            data = xml.dom.minidom.parseString(data)
            data = data.getElementsByTagName(etype)[0]
            if etype == 'node':
                data = self._DomParseNode(data)
            elif etype == 'way':
                data = self._DomParseWay(data)
            elif etype == 'relation':
                data = self._DomParseRelation(data)
            elif etype == 'changeset':
                data = self._DomParseChangeset(data)
                
            data[u'type'] = etype
            
        return data    
                
                
    #######################################################################
    # Internal dom functions - Borrowed from OsmApi                       #
    #######################################################################
    
    def _DomGetAttributes(self, DomElement):
        """ Returns a formated dictionnary of attributes of a DomElement. """
        result = {}
        for k, v in DomElement.attributes.items():
            if k == u"uid"         : v = int(v)
            elif k == u"changeset" : v = int(v)
            elif k == u"version"   : v = int(v)
            elif k == u"id"        : v = int(v)
            elif k == u"lat"       : v = float(v)
            elif k == u"lon"       : v = float(v)
            elif k == u"open"      : v = v=="true"
            elif k == u"visible"   : v = v=="true"
            elif k == u"ref"       : v = int(v)
            result[k] = v
        return result            
        
    def _DomGetTag(self, DomElement):
        """ Returns the dictionnary of tags of a DomElement. """
        result = {}
        for t in DomElement.getElementsByTagName("tag"):
            k = t.attributes["k"].value
            v = t.attributes["v"].value
            result[k] = v
        return result

    def _DomGetNd(self, DomElement):
        """ Returns the list of nodes of a DomElement. """
        result = []
        for t in DomElement.getElementsByTagName("nd"):
            result.append(int(int(t.attributes["ref"].value)))
        return result            

    def _DomGetMember(self, DomElement):
        """ Returns a list of relation members. """
        result = []
        for m in DomElement.getElementsByTagName("member"):
            result.append(self._DomGetAttributes(m))
        return result

    def _DomParseNode(self, DomElement):
        """ Returns NodeData for the node. """
        result = self._DomGetAttributes(DomElement)
        result[u"tag"] = self._DomGetTag(DomElement)
        return result

    def _DomParseWay(self, DomElement):
        """ Returns WayData for the way. """
        result = self._DomGetAttributes(DomElement)
        result[u"tag"] = self._DomGetTag(DomElement)
        result[u"nd"]  = self._DomGetNd(DomElement)        
        return result
    
    def _DomParseRelation(self, DomElement):
        """ Returns RelationData for the relation. """
        result = self._DomGetAttributes(DomElement)
        result[u"tag"]    = self._DomGetTag(DomElement)
        result[u"member"] = self._DomGetMember(DomElement)
        return result

    def _DomParseChangeset(self, DomElement):
        """ Returns ChangesetData for the changeset. """
        result = self._DomGetAttributes(DomElement)
        result[u"tag"] = self._DomGetTag(DomElement)
        return result
                
# class OsmPlanet
