from argparse import ArgumentParser
import random

class SolarSystem():
   parser = ArgumentParser()
   parser.add_argument( '-s', '--stars', type=int, default=-1,
                        help='Number of stars in the system' )
   parser.add_argument( '-p', '--planets', type=int, default=-1,
                        help='Number of planets in the system' )
   parser.add_argument( '-n', '--natural-features', type=int, default=-1,
                        help='Number of natural features in the system' )
   parser.add_argument( '-t', '--tech-features', type=int, default=-1,
                        help='Number of technological features in the system' )
   parser.add_argument( '-i', '--infra-features', type=int, default=-1,
                        help='Number of infrastructure features in the system' )
   parser.add_argument( '-f', '--faction', type=list, default=['human'],
                        help='Who owns property in the system' )
   parser.add_argument( '-T', '--tech-level', type=int, default=-1,
                        help='Maximum tech level in the system' )
   parser.add_argument( '-D', '--danger-level', type=int, default=-1,
                        help='Maximum danger level in the system' )
   parser.add_argument( '-I', '--infra-level', type=int, default=-1,
                        help='How much infrastructure is it in the system' )
   parser.add_argument( '-H', '--habitability-level', type=int, default=-1,
                        help='How habitable is it in the system' )
   parser.add_argument( '-S', '--star-type', type=str, default='random',
                        choices=['random', 'yellow', 'red giant',
                                 'white dwarf', 'neutron' ],
                        help='Preferred star type in the system' )
   

   def __init__( self,
                 Stars=None,Planets=None, NaturalFeatures=None, TechFeatures=None,
                 InfraFeatures=None ):
      print "Generating SolarSystem"
      self.args = self.parser.parse_args()
      self.Stars = Stars or []
      self.Planets = Planets or []
      self.NaturalFeatures = NaturalFeatures or []
      self.TechFeatures = TechFeatures or []
      self.InfraFeatures = InfraFeatures or []

      self.star_reqs = {}
      self.planet_reqs = {}
      self.feature_reqs = {}

      self.orbits = []

      self.generateSystemRequirements( self.Stars, self.Planets,
                                       self.NaturalFeatures, 
                                       self.TechFeatures,
                                       self.InfraFeatures )

      #### Begin Expaned Star System Generation ####
      self.generateStarSystemFeatures()
      self.placeKnownComponents()
      self.generateWorlds()
      self.generateSatallites()
      self.designateMainWorld()

   def generateSystemRequirements( self, Stars, Planets, NaturalFeatures, 
                                   TechFeatures, InfraFeatures ):
      """ Accept input objects that the system must satisfy the requirements of """
      for i,star in enumerate( Stars ):
         self.star_reqs[i].update( star.star_reqs )
      for i,planet in enumerate( Planets ):
         self.planet_reqs[i].update( planet.planet_reqs )

   def generateStarSystemFeatures( self ):
      self.systemNature()
      self.primaryStarType()
      self.companionTypeAndOrbit()
      self.numberOfOrbits()
      self.zoneDetermination()
      self.capturedPlanetsAndEmptyOrbits()
      self.gasGiants()
      self.planetoids()

   def placeKnownComponents( self ):
      self.placeGasGiants()
      self.placePlanetoids()

   def generateWorlds( self ):
      for orbit in orbits:
         if not orbit.occupied:
            orbit.generateWorld()
   
class Orbit(object):
   occupied = False
   zone = None
   body = None

   def generateWorld( self ):
      


class SolarObjectBase(object):
   reqs = {}
   body_type = None
   def __init__( self, reqs={} ):
      self.reqs = reqs or {}
      for key,value in reqs.items():
         setattr( self, key, value )

   @property
   def name( self ):
      return "%s" % self.body_type

class Star( SolarObjectBase ):
   body_type = 'star'
   star_type = 'yellow'
   star_types = [ 'yellow', 'red giant', 'white dwarf', 'neutron' ]

   @property
   def name( self ):
      return '%s %s' % ( self.star_type, self.body_type )
      
class World( SolarObjectBase ):
   body_type = 'world'
   size = None
   atmosphere = None
   hydrogrophy = None
   population = None
   num_of_satallites = None

   @property
   def name( self ):
      return '%s %s %s %s' % ( size, hydrogrophy, atmosphere, population )



if __name__ == '__main__':
   var = 'hey'
   lastVar = ''
   while var:
      var = raw_input("Please enter something: ")
      raw = var.strip(' \t\n\r')
      import sys
      sys.argv = sys.argv[:1] + raw.split( ' ' )

      system = SolarSystem()
      lastVar = var
   


