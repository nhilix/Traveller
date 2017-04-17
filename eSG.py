from argparse import ArgumentParser
import random, copy, json, pprint

def D( dice ):
   result = 0
   for d in range( dice ):
      roll = int( random.random() * 6 ) + 1
      result += roll
   return result
   

class SolarSystem():
   def __init__( self,
                  Stars=None,Planets=None, NaturalFeatures=None, TechFeatures=None,
                 InfraFeatures=None ):
      #print "Generating SolarSystem"
      self.Stars = Stars or []
      self.Planets = Planets or []
      self.NaturalFeatures = NaturalFeatures or []
      self.TechFeatures = TechFeatures or []
      self.InfraFeatures = InfraFeatures or []

      self.star_reqs = {}
      self.planet_reqs = {}
      self.feature_reqs = {}

      self.system_nature = None
      self.primary_star = None
      self.primary_world = None

      self.generateSystemRequirements( self.Stars, self.Planets,
                                       self.NaturalFeatures, 
                                       self.TechFeatures,
                                       self.InfraFeatures )

      #### Begin Expaned Star System Generation ####
      self.generateStarSystemFeatures()
      self.generateWorlds()
      self.generateSatallites()
      self.designateMainWorld()
      
      #if self.primary_world:
      #   print self.primary_world.fullName
      #self.primary_star.printBody()

   def generateSystemRequirements( self, Stars, Planets, NaturalFeatures, 
                                   TechFeatures, InfraFeatures ):
      """ Accept input objects that the system must satisfy the requirements of """
      for i,star in enumerate( Stars ):
         self.star_reqs[i].update( star.star_reqs )
      for i,planet in enumerate( Planets ):
         self.planet_reqs[i].update( planet.planet_reqs )

   def generateStarSystemFeatures( self ):
      self.systemNature()
      self.createStars()
      self.capturedPlanetsAndEmptyOrbits()
      self.gasGiantsAndPlanetoids()

   def generateWorlds( self ):
      for orbit in self.primary_star.orbits:
         if not orbit.occupied:
            orbit.generateWorld()
      binary = self.primary_star.binary
      if binary:
         for orbit in binary.orbits:
            if not orbit.occupied:
               orbit.generateWorld()
      trinary = self.primary_star.trinary
      if trinary:
         for orbit in trinary.orbits:
            if not orbit.occupied:
               orbit.generateWorld()

   def generateSatallites( self ):
      for orbit in self.primary_star.orbits:
         orbit.numberOfSatallites()
         orbit.generateSatallites()

   def designateMainWorld( self ):
      """ Choose the most appropriate world to be the 'main_world' """
      # Get any body that is not a ring satallite, a star or gas giant
      possibleWorlds = self.primary_star.getPossibleMainWorlds()

      if len( possibleWorlds ) > 0:
         # Sort by population, largest first, then pick only worlds with the largest population
         possibleWorlds = sorted( possibleWorlds, key=lambda world: world.population, reverse=True )
         possibleWorlds = [ world for world in possibleWorlds 
                                   if world.population == possibleWorlds[0].population ] 
         # If there is more than one with the largest population then pick the one in the habitable zone
         # failing that, pick the clostest to the primary star.
         if len( possibleWorlds ) > 1:
            habitableWorlds = [ world for world in possibleWorlds
                                       if world.orbit.zone == 'H' ]
            if len( habitableWorlds ) == 1:
               mainWorld = habitableWorlds[0]
            else:
               mainWorld = sorted( possibleWorlds, key=lambda world: world.primaryOrbit )[0]
         else:
            mainWorld = possibleWorlds[0]
         mainWorld.is_main_world = True
         self.primary_world = mainWorld

      if self.primary_world:
         self.primary_world.determineAdditionalCharacteristics()
      for world in self.primary_star.getPossibleMainWorlds():
         if not world == self.primary_world:
            world.determineAdditionalCharacteristics()


   def systemNature( self ):
      roll = D(2)
      if roll < 8:
         roll = 'solo'
      elif roll < 12:
         roll = 'binary'
      elif roll == 12:
         roll = 'trinary'
      self.system_nature = roll

   def createStars( self ):
      self.primary_star = PrimaryStar( self.system_nature )

   def capturedPlanetsAndEmptyOrbits( self ):
      self.primary_star.createEmptyOrbits()
      self.primary_star.capturedPlanets()

      binary = self.primary_star.binary
      if binary:
         binary.createEmptyOrbits()
         binary.capturedPlanets()
      
      trinary = self.primary_star.trinary
      if trinary:
         trinary.createEmptyOrbits()
         trinary.capturedPlanets()

   def gasGiantsAndPlanetoids( self ):
      self.primary_star.createGasGiants()
      self.primary_star.createPlanetoids()

      binary = self.primary_star.binary
      if binary:
         binary.createGasGiants()
         binary.createPlanetoids()

      trinary = self.primary_star.trinary
      if trinary:
         trinary.createGasGiants()
         trinary.createPlanetoids()

class Orbit(object):
   def __init__( self,  star, number ):
      self.star =  star
      self.number = number
      self.occupied = False
      if self.zone in ['-','_']:
         self.occupied = True
      self.body = None

   def generateWorld( self, deviation=0 ):
      self.occupied = True
      self.body = World( self.star, self, deviation=deviation )

   def generateGasGiant( self ):
      self.occupied = True
      self.body = GasGiant( self.star, self, self.zone )
      self.star.num_of_gas_giants = self.star.num_of_gas_giants + 1

   def numberOfSatallites( self ):
      if self.body:
         self.body.numberOfSatallites()

   def generateSatallites( self ):
      if self.body:
         self.body.generateSatallites()

   def determineAdditionalCharacteristics( self ):
      if self.body:
         self.body.determineAdditionalCharacteristics()

   def printBody( self ):
      if self.name:
         print self.name
      if self.body:
         self.body.printBody()
   def getJson( self ):
      if self.body:
         return self.body.getJson()
      return {}
   @property
   def prefix( self ):
      bodyPrefix = ''
      if self.body:
         bodyPrefix = self.body.prefix
      if isinstance( self.star, BinaryStar ):
         bodyPrefix = self.star.prefix + bodyPrefix
      return bodyPrefix + '{:-<4}'.format( str( self.number ) + 's' + self.zone.lower() )
   @property
   def name( self ):
      if self.body == None and self.occupied:
         return self.prefix
      return ''
   @property
   def zone( self ):
      star = self.star
      if not isinstance( star, Star ):
         return '_'
      zones = star._zones[min(star.size, 5)][star.star_class]
      if self.number >= len( zones ):
         return 'O'
      else:
         return zones[ self.number ]

class PlanetoidBelt( Orbit ):
   def __init__( self, star, number ):
      super( PlanetoidBelt, self ).__init__( star, number )
      self.occupied = True
      self.body = PlanetoidBase()
      self.body.orbit = self
   
   @property
   def prefix( self ):
      return self.star.prefix + '{:-<4}'.format( str( self.number ) + 's' + self.zone.lower() )
   @property
   def name( self ):
      zone = ''
      if self.zone == 'O':
         zone = 'outter '
      if self.zone == 'I':
         zone = 'inner '
      return '%splanetoid belt' % zone
   def printBody( self ):
      print self.prefix, self.name
   def getJson( self ):
      return { 'planetoid belt' : {
                     'zone' : self.zone,
                     'occupied' : self.occupied,
                  } 
             }


class SolarObjectBase(object):
   def __init__( self, reqs={} ):
      self.reqs = reqs or {}
      self.size = None
      for key,value in reqs.items():
         setattr( self, key, value )

   def getPossibleMainWorlds( self ):
      possibleWorlds = []
      for o in self.orbits:
         if o.body:
            for world in o.body.getPossibleMainWorlds():
               possibleWorlds.append( world )
      return possibleWorlds

   def printBody( self ):
      print self.prefix, self.name
      for o in self.orbits:
         o.printBody()
   def getJson( self ):
      data = {}
      for o in self.orbits:
         data.update( { o.number : o.getJson() } )
      return { self.name : data }

   @property
   def fullName( self ):
      return self.prefix + ' ' + self.name
   @property
   def name( self ):
      return "%s" % self.body_type
   @property
   def body_type( self ):
      return 'solarobjectbase'

class Star( SolarObjectBase ):
   _star_types = {
         'O' : 'blue white',
         'B' : 'blue',
         'A' : 'white',
         'M' : 'red', 
         'K' : 'orange',
         'G' : 'yellow',
         'F' : 'yellow-white',
      }
   _star_sizes = {
         0   : 'bright supergiant',
         1   : 'weaker supergiant',
         2   : 'bright giant',
         3   : 'giant',
         4   : 'subgiant',
         5   : 'main sequence',
         6   : 'dwarf',
      }
   _zones = [
         { #  SIZE 0 
            "B0" : [ '-' , '_', '_', '_', '_', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O' ],
            "B5" : [ '-' , '_', '_', '_', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "A0" : [ '-' , '-', '_', '_', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "A5" : [ '-' , '-', '_', '_', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "F0" : [ '-' , '-', '-', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O' ],
            "F5" : [ '-' , '-', '-', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O' ],
            "G0" : [ '-' , '-', '-', '-', '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "G5" : [ '-' , '-', '-', '-', '-', '_', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "K0" : [ '-' , '-', '-', '-', '-', '-', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "K5" : [ '-' , '-', '-', '-', '-', '-', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "M0" : [ '-' , '-', '-', '-', '-', '-', '-',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "M5" : [ '-' , '-', '-', '-', '-', '-', '-', '-',
                           'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
         },
         { # SIZE 1
            "B0" : [ '-' , '_', '_', '_', '_', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O' ],
            "B5" : [ '-' , '_', '_', '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O' ],
            "A0" : [ '-' , '_', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O' ],
            "A5" : [ '-' , '_', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "F0" : [ '-' , '_', '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "F5" : [ '-' , '_', '_', '_', 
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "G0" : [ '-' , '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "G5" : [ '-' , '-', '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "K0" : [ '-' , '-', '-', '-', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "K5" : [ '-' , '-', '-', '-', '-', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O' ],
            "M0" : [ '-' , '-', '-', '-', '-', '-',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O' ],
            "M5" : [ '-' , '-', '-', '-', '-', '-', '-',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
         },
         { # SIZE 2
            "B0" : [ '-' , '_', '_', '_', '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O' ],
            "B5" : [ '-' , '_', '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
            "A0" : [ '-' , '_', '_', 
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "A5" : [ '-' , '_', 
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O' ],
            "F0" : [ '-' , '_',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O' ],
            "F5" : [ '-' , '_', 
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O' ],
            "G0" : [ '-' , '_',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O' ],
            "G5" : [ '-' , '_',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O' ],
            "K0" : [ '-' , '_',
                           'I', 'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "K5" : [ '-' , '-', '_',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "M0" : [ '-' , '-', '-', '-',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O' ],
            "M5" : [ '-' , '-', '-', '-', '-', '-',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O' ],
         },
         { # SIZE 3
            "B0" : [ '-' , '_', '_', '_', '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O' ],
            "B5" : [ '-' , '_', '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O' ],
            "A0" : [ '-' , 
                           'I', 'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O' ],
            "A5" : [ '-' , 
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O' ],
            "F0" : [ '-' ,
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "F5" : [ '-' ,
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "G0" : [ '-' ,
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "G5" : [ '-' ,
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O' ],
            "K0" : [ '-' ,
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O' ],
            "K5" : [ '-' ,
                           'I', 'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O' ],
            "M0" : [ '-' , '_',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O' ],
            "M5" : [ '-' , '-', '-', '-',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
         },
         { # SIZE 4
            "B0" : [ '_' , '_', '_', '_', '_', '_', '_',
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O' ],
            "B5" : [ '_' , '_', '_',
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O' ],
            "A0" : [ '_' , 
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O' ],
            "A5" : [ 
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "F0" : [
                           'I', 'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "F5" : [
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "G0" : [
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "G5" : [
                           'I', 'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "K0" : [
                           'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "K5" : [
                           'I', 'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "M0" : [
                           'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "M5" : [
                           'I', 'I', 'I',
                           'H',
                           'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
         },
         { # SIZE 5
            "B0" : [ '_' , '_', '_', '_', '_', '_',
                     'I', 'I', 'I', 'I', 'I', 'I',
                     'H',
                     'O' ],
            "B5" : [ '_' , '_', '_',
                     'I', 'I', 'I', 'I', 'I', 'I',
                     'H',
                     'O', 'O', 'O', 'O' ],
            "A0" : [ 'I', 'I', 'I', 'I', 'I', 'I', 'I',
                     'H',
                     'O', 'O', 'O', 'O', 'O', 'O' ],
            "A5" : [ 'I', 'I', 'I', 'I', 'I', 'I',
                     'H',
                     'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "F0" : [ 'I', 'I', 'I', 'I', 'I',
                     'H',
                     'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "F5" : [ 'I', 'I', 'I', 'I',
                     'H',
                     'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "G0" : [ 'I', 'I', 'I',
                     'H',
                     'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "G5" : [ 'I', 'I',
                     'H',
                     'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "K0" : [ 'I', 'I',
                     'H',
                     'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "K5" : [ 'H',
                     'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "M0" : [ 'H',
                     'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
            "M5" : [ 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O' ],
         },
      ]

   def __init__( self ):
      super( Star , self ).__init__()
      self.star_type = 'G'
      self.star_decimal = 0
      self.orbits = []
      self.max_usable_orbits = 0
      self.num_of_gas_giants = 0
      self.binary = None
      self.trinary = None

      self._type()
      self._decimal()
      self._size()
      self.createCompanions()
      self._orbits()
      self.placeCompanions()

   def _orbits( self ):
      maxOrbits = 14
      if self.size < 2: 
         maxOrbits = 15
      if isinstance( self, BinaryStar ):
         maxOrbits = self.orbit / 2
      self.orbits = [ Orbit( self, x ) for x in range( maxOrbits ) ]
      for o in self.orbits:
         o.occupied = True
      roll = D(2)
      if self.size == 3:
         roll = roll + 4
      elif self.size <= 2:
         roll = roll + 8
      if self.star_type == 'M':
         roll = roll - 4
      elif self.star_type == 'K':
         roll = roll - 2
      if roll < 0:
         roll = 0
      if roll > maxOrbits - 1:
         roll = maxOrbits - 1
      self.max_usable_orbits = roll
      for x in range( roll ):
         self.orbits[ x ] = Orbit( self, x )

   def _decimal( self ):
      roll = D(1)
      if roll <= 3:
         decimal = 0
      else:
         decimal = 5
      self.star_decimal = decimal

   def createCompanions( self ):
      if self.system_nature == 'solo':
         return
      if self.system_nature == 'binary':
         self.binary = BinaryStar( self )
      if self.system_nature == 'trinary':
         self.binary = BinaryStar( self )
         self.trinary = TrinaryStar( self )

   def placeCompanions( self ):
      for companion in [ self.binary, self.trinary ]:
         if companion:
            try:
               orbit = self.orbits[ companion.orbit ]
            except IndexError:
               for x in range( 1 + companion.orbit - len(self.orbits) ):
                  self.orbits.append( Orbit( self, x + len(self.orbits) ) )
            orbit = self.orbits[ companion.orbit ] = Orbit( self, companion.orbit )
            orbit.occupied = True
            orbit.body = companion
            deadZone = ( companion.orbit / 2, companion.orbit * 2 )
            for o in range( deadZone[0], deadZone[1] ):
               if o >= len(self.orbits):
                  continue
               orbit = self.orbits[ o ]
               orbit.occupied = True
   
   def createGasGiants( self ):
      roll = D(2) 
      if roll > 9:
         return
      roll = D(2)
      num_gas_giants = roll
      if roll < 4:
         num_gas_giants = 1
      elif roll < 6:
         num_gas_giants = 2
      elif roll < 8:
         num_gas_giants = 3
      elif roll < 11:
         num_gas_giants = 4
      else:
         num_gas_giants = 5

      emptyOs = self.emptyOrbits()
      _emptyOs = copy.copy(emptyOs)
      for o in _emptyOs:
         if o.zone not in [ 'O', 'H' ]:
            emptyOs.remove( o )
      if len( emptyOs ) == 0 and not len( _emptyOs ) == 0:
         emptyOs = copy.copy(_emptyOs)
      if num_gas_giants > len( emptyOs ):
         num_gas_giants = len( emptyOs )

      for x in range( num_gas_giants ):
         roll = 0
         if len( emptyOs ) > 1:
            sections = int( len( emptyOs ) / 6 ) + bool( len( emptyOs ) % 6 )
            roll = D(1)
            while roll > sections:
               roll = D(1)
            section = roll - 1
            if roll == sections:
               sections = len( emptyOs ) % 6
               if sections == 0:
                  sections = 5
            else:
               sections = 5
            roll = D(1)
            while roll > sections:
               roll = D(1)
            roll = roll - 1 + section * 6

         orbit = emptyOs[ roll ]
         orbit.generateGasGiant()
         emptyOs.remove( orbit )

   def createPlanetoids( self ):
      roll = D(2) - self.num_of_gas_giants
      if roll > 6:
         return
      roll = D(2) - self.num_of_gas_giants 
      if roll < 1:
         num_of_planetoids = 3
      elif roll < 7:
         num_of_planetoids = 2
      else:
         num_of_planetoids = 1

      emptyOs = self.emptyOrbits()
      if num_of_planetoids > len( emptyOs ):
         num_of_planetoids = len( emptyOs )
         
      for x in range( num_of_planetoids ):
         gasGiants = [ g for g in self.orbits if isinstance( g.body, GasGiant ) ]
         for gasG in gasGiants:
            if not self.orbits[ gasG.number - 1 ].occupied:
               self.orbits[ gasG.number - 1 ] = PlanetoidBelt( self, gasG.number - 1 )
               break
         else:
            emptyOrbitNums = [ orbit.number for orbit in emptyOs ]
            roll = int( random.random() * len( emptyOrbitNums ) )
            roll = emptyOrbitNums[ roll ]
            self.orbits[ roll ] = PlanetoidBelt( self, roll )

   def createEmptyOrbits( self ):
      for o in self.orbits:
         if o.zone == '-':
            o.occupied = True
      roll = D(1)
      if roll > 4:
         num_empty = D(1)
         if num_empty < 3:
            num_empty = 1
         elif num_empty == 3:
            num_empty = 2
         else:
            num_empty = 3
         for x in range( num_empty ):
            if self.emptyOrbits():
               roll = self.getValidRoll( 2 )
               if roll == 0:
                  continue
               self.orbits[ roll ].occupied = True 

   def capturedPlanets( self ):
      if len(self.orbits) < 2:
         return
      roll = D(1)
      if roll > 4:
         num_of_caps = D(1)
         if num_of_caps < 3:
            num_of_caps = 1
         elif num_of_caps < 5:
            num_of_caps = 2
         else:
            num_of_caps = 3
         for x in range( num_of_caps ):
            if self.emptyOrbits():
               roll = self.getValidRoll( 2 )
               if roll == 0:
                  continue
               deviation = 0.1 * ( D(2) - 7.0 )
               self.orbits[roll].generateWorld( deviation=deviation )

   def getValidRoll( self, num ):
      roll = D(num)
      emptyOs = self.emptyOrbits()
      _emptyOs = copy.copy( emptyOs )
      for emptyO in _emptyOs:
         if emptyO.number == 0:
            emptyOs.remove( emptyO )
         if emptyO.number == 1:
            emptyOs.remove( emptyO )
      if len( emptyOs ) == 0:
         return 0
      if not roll in [ emptyO.number for emptyO in emptyOs ]:
         roll = self.getValidRoll( num )
      return roll

   def emptyOrbits( self ):
      orbits = [ orbit for orbit in self.orbits if not orbit.occupied ]
      return orbits


   @property
   def name( self ):
      return '%s %s(%s)  %s' % ( self._star_sizes[ self.size ],
                               self._star_types[ self.star_type ], 
                               self.star_class, self.body_type )
   @property
   def body_type( self ):
      return 'Star'
   @property
   def star_class( self ):
      return '%s%d' % ( self.star_type, self.star_decimal )

class PrimaryStar( Star ):
   def __init__( self, system_nature=None ):
      self.system_nature = system_nature
      super( PrimaryStar, self ).__init__()

   def _type( self ):
      roll = D(2)
      self.star_type_roll = roll
      star_type = roll
      if roll < 2:
         star_type = 'B'
      elif roll < 3:
         star_type = 'A'
      elif roll < 8:
         star_type = 'M'
      elif roll < 9:
         star_type = 'K'
      elif roll < 10:
         star_type = 'G'
      else:
         star_type = 'F'
      self.star_type = star_type

   def _size( self ):
      roll = D(2)
      self.size_roll = roll
      size = roll
      if roll > 4 and roll < 11:
         size = 5
      elif roll == 11:
         size = 6
      elif roll == 12:
         size = 6
      if size == 4 and self.star_class in [ 'K5', 'M0', 'M5' ]: 
         size = 5
      if size == 6 and self.star_class in [ 'B0', 'B5', 'A0', 'A5', 'M0', 'M5', 
                                            'K0', 'K5', 'G0', 'G5', 'F0' ]:
         size = 5
      self.size = size

   def printBody( self ):
      print self.name
      for o in self.orbits:
         o.printBody()
   def getJson( self ):
      data = {}
      for o in self.orbits:
         data.update( { o.number : o.getJson() } )
      return { self.name : data }

   @property
   def prefix( self ):
      return ''
         
class BinaryStar( Star ):
   orbit_roll_modifier = 0

   def __init__( self, primary_star=None ):
      self.star  = primary_star 
      self.system_nature = 'solo'
      self.orbit = None

      self._orbit()
      super( BinaryStar, self ).__init__()
      if self.orbit >= 12:
         self._system_nature()
         self.createCompanions()
         self.placeCompanions()

   def _type( self ):
      roll = D(2) + self.star.star_type_roll
      self.star_type_roll = roll
      star_type = roll
      if roll == 2:
         star_type = 'A'
      elif roll < 5:
         star_type = 'F'
      elif roll < 7:
         star_type = 'G'
      elif roll < 9:
         star_type = 'K'
      else:
         star_type = 'M'
      self.star_type = star_type

   def _size( self ):
      roll = D(2) + self.star.size_roll
      self.size_roll = roll
      size = roll
      if roll < 4 and roll < 7:
         size = 4
      elif roll < 9:
         size = 5
      elif roll == 9:
         size = 6
      else:
         size = 6
      if size == 4 and self.star_class in [ 'K5', 'M0', 'M5' ]: 
         size = 5
      if size == 6 and self.star_class in [ 'B0', 'B5', 'A0', 'A5', 'M0', 'M5', 
                                            'K0', 'K5', 'G0', 'G5', 'F0' ]:
         size = 5
      self.size = size

   def _orbit( self ):
      roll = D(2) + self.orbit_roll_modifier
      orbit = roll - 3
      if isinstance(self.star, BinaryStar):
         orbit = orbit - 4
      if orbit < 0:
         orbit = 0
      if orbit >= 4:
         orbit = orbit + D(1)
      self.orbit = orbit

   def _system_nature( self ):
      roll = D(2) 
      if roll < 8:
         roll = 'solo'
      elif roll <= 12:
         roll = 'binary'
      self.system_nature = roll

   def numberOfSatallites( self ):
      for orbit in self.orbits:
         orbit.numberOfSatallites()
   def generateSatallites( self ):
      for orbit in self.orbits:
         orbit.generateSatallites()

   @property
   def prefix( self ):
      return self.star.prefix + '{:-<4}'.format( str( self.orbit ) + 's' + \
             self.star.orbits[ self.orbit ].zone.lower() )

class TrinaryStar( BinaryStar ):
   orbit_roll_modifier = 4
 
class PlanetoidBase( SolarObjectBase ):
   def __init__( self ):
      super( PlanetoidBase, self ).__init__()
      self.star = None
      self.atmosphere = None
      self.hydrography = None
      self.population = None
      self.government = 0

      self.law = 0
      self.star_port = 'X'
      self.space_port = 'Y'
      self.tech = 0
      self.trade_classification = ''
      self.scout_base = False
      self.naval_base = False
      self.facilities = []
      
      self.orbit = None
      self.deviation = 0
      self.is_main_world = False

      self.orbits = []

   def _atmosphere( self ):
      """ Determine the atmosphere present """
      pass
   def _hydrography( self ):
      """ Determine the hydrography """
      pass
   def _population( self ):
      """ Determine the population level """
      pass

   def numberOfSatallites( self ):
      pass
   def generateSatallites( self ):
      pass
   def getPossibleMainWorlds( self ):
      pass

   def getPossibleMainWorlds( self ):
      possibleWorlds = []
      for o in self.orbits:
         if o.body:
            for world in o.body.getPossibleMainWorlds():
               possibleWorlds.append( world )
      return possibleWorlds

   def printBody( self ):
      print self.prefix, self.name
      for orbit in sorted( self.orbits, key=lambda orbit: orbit.number ):
         orbit.printBody()
   def getJson( self ):
      data = {
            'size'        : self.size,
            'atmosphere'  : self.atmosphere,
            'hydrography' : self.hydrography,
            'population'  : self.population,
            'government'  : self.government,
            'law'         : self.law,
            'starport'    : self.star_port,
            'spaceport'   : self.space_port,
            'tech'        : self.tech,
            'trade_class' : self.trade_classification,
            'scout_base'  : self.scout_base,
            'naval_base'  : self.naval_base,
            'facilities'  : self.facilities,
            'deviation'   : self.deviation,
            'main_world'  : self.is_main_world,
         }
      for orbit in sorted( self.orbits, key=lambda orbit: orbit.number ):
         data.update( { orbit.number : orbit.getJson() } )
      return { self.body_type : data }
      
   @property
   def primaryOrbit( self ):
      if hasattr( self.star, 'orbit' ):
         return self.star.orbit
      return self.orbit.number
   @property
   def prefix( self ):
      return ''
   @property
   def name( self ):
      return self.body_type
   @property
   def body_type( self ):
      return 'Planetoid'
      
class World( PlanetoidBase ):
   _sizes = {
         0   : 'planetiod belt',
         'R' : 'ring',
         'S' : 'small',
         1   : '1000mi radius',
         2   : '2000mi radius',
         3   : '3000mi radius',
         4   : '4000mi radius',
         5   : '5000mi radius',
         6   : '6000mi radius',
         7   : '7000mi radius',
         8   : '8000mi radius',
         9   : '9000mi radius',
         10  : '10000mi radius',
         'SGG': 'small',
         'LGG': 'large',
      }
   _atmospheres = [
         'no', 
         'a trace',
         'a very thin, tainted',
         'a very thin',
         'a thin, tainted',
         'a thin',
         'a standard',
         'a standard, tainted',
         'a dense',
         'a dense, tainted',
         'an exotic',
         'a corrosive',
         'a insidious',
         'a dense, high',
         'an ellipsoid',
         'a thin, low',
         ]
   _hydrographies = [
         '0%',
         '10%',
         '20%',
         '30%',
         '40%',
         '50%',
         '60%',
         '70%',
         '80%',
         '90%',
         '100%',
         ]
   _populations = [
         'zero',
         'tens of',
         'hundreds of',
         'thousands of',
         'tens of thousands of',
         'hundreds of thousands of',
         'millions of',
         'tens of millions of',
         'hundreds of millions of',
         'billions of',
         'tens of billions of',
         ]
   _governments = [
         'no government',
         'company',
         'participating democracy',
         'self-perpetuating oligarchy',
         'representitive democracy',
         'feudal technocracy',
         'captive government',
         'balkanization',
         'civil service bureaucracy',
         'impersonal bureaucracy',
         'charismatic dictator',
         'non-charismatic leader',
         'charismatic oligarchy',
         'religious dictatorship',
         ]
   _laws = [
         'a lawless',
         'a nearly lawless',
         'a somewhat lawless',
         'a fairly moderate',
         'a moderate',
         'a moderately enforced',
         'an enforced',
         'a well enforced',
         'a strongly enforced',
         'an oppressive',
         'a highly oppressive',
         'an extremely oppressive',
          ]
   _star_ports = {
         'A' : 'an excellent quality starport',
         'B' : 'a good quality starport',
         'C' : 'a routine quality starport',
         'D' : 'a poor quality starport',
         'E' : 'a frontier installation',
         'X' : 'no starport',
      }
   _space_ports = {
         'F' : 'a good quality spaceport',
         'G' : 'a poor quality spaceport',
         'H' : 'primitive facilities',
         'Y' : 'no spaceport',
      }
   _tech_mods = {
         'starport'   : {
               'A' :  6,
               'B' :  4,
               'C' :  2,
               'D' :  0,
               'E' :  0,
               'X' : -4,
            },
         'size'       : [
               2, 2, 1, 1, 1,
               0, 0, 0, 0, 0, 0,
            ],
         'atmosphere' : [
               1, 1, 1, 1,
               0, 0, 0, 0, 0, 0,
               1, 1, 1, 1, 1, 0,
            ],
         'hydrography': [
               0, 0, 0, 0, 0, 0,
               0, 0, 0, 1, 2,
            ],
         'population' : [
               0, 1, 1, 1, 1, 1,
               0, 0, 0, 2, 4,
            ],
         'government' : [
               1, 0, 0, 0, 0, 1,
               0, 0, 0, 0, 0, 0,
               2, 0, 0,
            ],
      }


   def __init__( self, star, orbit, deviation=0 ):
      """ Generate A Random World inside  'zone' """
      super( World, self ).__init__()
      self.num_of_satallites = None
      self.star = star
      self.orbit = orbit
      self.deviation = deviation
       
      self._size()
      self._atmosphere()
      self._hydrography()
      self._population()

   def _size( self ):
      roll = D(2) - 2;
      orbit = self.orbit
      if orbit.number == 0:
         roll = roll - 5
      elif orbit.number == 1:
         roll = roll - 4
      elif orbit.number == 2:
         roll = roll - 2
      if self.star.star_type == 'M':
         roll = roll - 2
      if roll <= 0:
         size = 'S'
      else:
         size = roll
      self.size = size

   def _atmosphere( self ):
      size = self.size
      if size == 'S':
         size = 0
      roll = D(2) - 7 + size
      if self.orbit.zone == 'I':
         roll = roll - 2
      if self.orbit.zone == 'O':
         roll = roll - 4
      if size == 0:
         roll = 0

      if roll < 0:
         roll = 0
      if roll > 15:
         roll = 15

      self.atmosphere = roll
      if self.orbit.zone == 'O':
         z = self.star.orbits[ max(self.orbit.number - 2, 0) ].zone
         if z == 'O' or z == 'H':
            exotic = D(2)
            if exotic == 12:
               self.atmosphere = 10
   
   def _hydrography( self ):
      size = self.size
      if size == 'S':
         size = 0
      roll = D(2) - 7 + size
      if self.orbit.zone == 'O':
         roll = roll - 2
      if self.atmosphere <= 1 or self.atmosphere >= 10:
         roll = roll - 4
      if self.orbit.zone == 'I':
         roll = 0
      if size <= 1:
         roll = 0
      if roll < 0:
         roll = 0
      if roll > 10:
         roll = 10
      self.hydrography = roll

   def _population( self ):
      roll = D(2) - 2
      if self.orbit.zone == 'I':
         roll = roll - 5
      if self.orbit.zone == 'O':
         roll = roll - 3
      if not self.atmosphere in [ 0, 5, 6, 8 ]:
         roll = roll - 2
      if roll < 0:
         roll = 0
      if roll > 10:
         roll = 10
      self.population = roll

   def numberOfSatallites( self ):
      if not self.size == 'S':
         self.num_of_satallites = D(1) - 3
      else:
         self.num_of_satallites = 0
   def generateSatallites( self ):
      for x in range( self.num_of_satallites ):
         satallite_size = self.size
         if satallite_size == 'S':
            satallite_size = 0
         size = satallite_size - D(1)
         if size == 0:
            size = 'R'
         if size < 0:
            size = 'S'

         multiple = 1
         roll = D(2)
         if roll > 7:
            multiple = 5
         orbitNum = self.getValidSatalliteRoll( multiple, size )

         self.orbits.append( Orbit( self, orbitNum ) )
         self.orbits[-1].occupied = True
         self.orbits[-1].body = Satallite( self, self.orbits[-1], size )

   def getValidSatalliteRoll( self, multiple, size ):
      # If ring, go in first 3 orbitals
      if size == 'R':
         roll = D(1)
         if roll < 4:
            roll = 1
         elif roll < 6:
            roll = 2
         else:
            roll = 3
         orbitNums =  [ o.number for o in self.orbits ]
         # if all 3 are taken, find first available orbit to put ring in
         if not (1 in orbitNums and 2 in orbitNums and 3 in orbitNums ):
            if roll in orbitNums:
               roll = self.getValidSatalliteRoll( multiple, size )
         else:
            for x in range( 100 ):
               if x not in orbitNums:
                  return x
         return roll
      # Table from Scouts (Book 6) Pg. 28
      roll = ( D(2) + 1 ) * multiple
      if roll in [ o.number for o in self.orbits ]:
         roll = self.getValidSatalliteRoll( multiple, size )
      return roll


   def _government( self ):
      self.government = min( max( 0, D(2) - 7 + self.population ), 13 )

   def _law( self ):
      self.law = min( max( 0, D(2) - 7 + self.government ), 11 )

   def _starPort( self ):
      roll = D(2)
      star_port = 'X'
      if roll < 5:
         star_port = 'A'
      elif roll < 7:
         star_port = 'B'
      elif roll < 9:
         star_port = 'C'
      elif roll < 10:
         star_port = 'D'
      elif roll < 12:
         star_port = 'E'
      self.star_port = star_port

   def _tech( self ):
      mod = 0
      mod += self._tech_mods['starport'][self.star_port]
      size = self.size if not ( self.size == 'R' or self.size == 'S' ) else 0
      mod += self._tech_mods['size'][size]
      mod += self._tech_mods['atmosphere'][self.atmosphere]
      mod += self._tech_mods['hydrography'][self.hydrography]
      mod += self._tech_mods['population'][self.population]
      mod += self._tech_mods['government'][self.government]
      self.tech = min( max( D(1) + mod, 0 ), 16 )

   def _trade( self ):
      def agricultural( self ):
         atmo  = self.atmosphere  in range(4,10)
         hydro = self.hydrography in range(4, 9)
         pop   = self.population  in range(5, 8)
         return 'agricultural ' if ( atmo and hydro and pop ) else ''
      def nonagricultural( self ):
         atmo  = self.atmosphere  <= 3
         hydro = self.hydrography <= 3
         pop   = self.population  >= 6
         return 'non-agricultural ' if ( atmo and hydro and pop ) else ''
      def industrial( self ):
         atmo  = self.atmosphere  in [0,1,2,4,7,9]
         pop   = self.population  >= 9
         return 'industrial ' if ( atmo and pop ) else ''
      def nonindustrial( self ):
         return 'non-industrial ' if self.population <= 6 else ''
      def rich( self ):
         atmo  = self.atmosphere  in [6,8]
         pop   = self.population  in range(6, 9)
         govt  = self.government  in range(4,10)
         return 'rich ' if ( atmo and pop and govt ) else ''
      def poor( self ):
         atmo  = self.atmosphere  in range(2, 6)
         hydro = self.hydrography <= 3
         return 'poor ' if ( atmo and hydro ) else ''
      def waterWorld( self ):
         return 'water ' if self.hydrography  == 10 else ''
      def desertWorld ( self ):
         atmo  = self.atmosphere  >= 2
         hydro = self.hydrography == 0
         return 'desert ' if ( atmo and hydro ) else ''
      def vacuumWorld( self ):
         return 'vacuum ' if self.atmosphere   ==  0 else ''
      def asteroidBelt( self ):
         return 'asteroid belt' if self.size  ==  0 else ''
      def iceCapped( self ):
         atmo  = self.atmosphere in [0,1]
         hydro = self.hydrography >= 1
         return 'ice-capped ' if ( atmo and hydro ) else ''
      self.trade_classification = '%s%s%s%s%s%s%s%s%s%s' % (
                                    rich( self ), poor( self ),
                                    industrial( self ), nonindustrial( self ),
                                    agricultural( self ), nonagricultural( self ),
                                    vacuumWorld( self ), iceCapped( self ),
                                    waterWorld( self ), desertWorld( self ) )

   def _bases( self ):
      mod = 0
      scout = False
      naval = False
      if self.star_port == 'C':
         mod = -1
      if self.star_port == 'B':
         mod = -2
      if self.star_port == 'A':
         mod = -3
      if not self.star_port in ['E','X']:
         roll = D(2) + mod
         if roll >= 7:
            scout = True
         if not self.star_port in ['C','D']:
            roll = D(2)
            if roll >= 8:
               naval = True
      self.scout_base = scout
      self.naval_base = naval

   def _subGovt( self ):
      roll = D(1)
      if self.main_world.government == 6:
         roll = 6
      if self.main_world.government >= 7:
         roll = roll + 1
         
      if roll >= 5:
         govt = 6
      else:
         govt = roll - 1

      if self.population == 0:
         govt = 0
      self.government = govt

   def _subLaw( self ):
      roll = D(1) - 3 + self.main_world.law
      if self.population == 0:
         roll = 0
      self.law = min( max( roll, 0 ), 11 )

   def _subFacilities( self ):
      def farming( self ):
         zone  = self.orbit.zone == 'H'
         atmo  = self.atmosphere in range(4,10)
         hydro = self.hydrography in range(4,9)
         pop   = self.population >= 2
         return ( zone and atmo and hydro and pop )
      def mining( self ):
         main_trade = self.main_world.trade_classification.split()
         for trade in main_trade:
            if 'industrial' == trade:
               if self.population >= 2:
                  return True
         return False
      def colony( self ):
         govt = self.government == 6
         pop  = self.population >= 5
         return ( govt and pop )
      def research( self ):
         roll = D(2)
         if self.main_world.tech >= 10:
            roll = roll + 2
         if self.main_world.tech <= 8 or self.population == 0:
            roll = 0
         if roll >= 11:
            return True
         return False
      def military( self ):
         roll = D(2)
         if self.main_world.population >= 8:
            roll = roll + 1
         if self.main_world.atmosphere == self.atmosphere:
            roll = roll + 2
         if self.main_world.naval_base or self.main_world.scout_base:
            roll = roll + 1
         if self.population == 0:
            roll = 0
         main_trade = self.main_world.trade_classification.split()
         for trade in main_trade:
            if 'poor' == trade:
               roll = 0
         if roll >= 12:
            return True
         return False
      facilities = []
      if farming( self ):
         facilities.append( 'farming' )
      if mining( self ):
         facilities.append( 'mining' )
      if colony( self ):
         facilities.append( 'colony' )
      if research( self ):
         facilities.append( 'research' )
      if military( self ):
         facilities.append( 'military' )
      self.facilities = facilities

   def _subTech( self ):
      self.tech = self.main_world.tech - 1
      if 'military' in self.facilities or 'research' in self.facilities:
         self.tech = self.tech + 1

   def _spacePort( self ):
      roll = D(1)
      if self.population >= 6:
         roll = roll + 2
      if self.population <= 1:
         roll = roll - 2
      roll = min( max( roll, 1 ), 6 )
      if roll < 3:
         space_port = 'Y'
      elif roll < 4:
         space_port = 'H'
      elif roll < 6:
         space_port = 'G'
      else:
         space_port = 'F'
      self.space_port = space_port

   def determineAdditionalCharacteristics( self ):
      if self.is_main_world:
         self._government()
         self._law()
         self._starPort()
         self._tech()
         self._trade()
         self._bases()
      else:
         self._subGovt()
         self._subLaw()
         self._subFacilities()
         self._subTech()
         self._spacePort()

   def getPossibleMainWorlds( self ):
      possibleWorlds = super( World, self ).getPossibleMainWorlds()
      if not self.size == 'R':
         possibleWorlds.append( self )
      return possibleWorlds


   @property
   def main_world( self ):
      if self.is_main_world:
         return self
      else:
         if isinstance( self.star, BinaryStar ):
            primary_world = [ x for x in self.star.star.getPossibleMainWorlds() if x.is_main_world ][0]
         else:
            primary_world = [ x for x in self.star.getPossibleMainWorlds() if x.is_main_world ][0]
         return primary_world

   @property
   def prefix( self ):
      return self.star.prefix + '{:-<4}'.format( str( self.orbit.number ) + 's' +
                                                 self.orbit.zone.lower() )
   @property
   def name( self ):
      primary = '(Primary TL%d) ' % self.tech if self.is_main_world else ''
      firstLine =  '%s %s%s covered in %s water\n' % (
            self._sizes[ self.size ], self.trade_classification, self.body_type,
            self._hydrographies[ self.hydrography ] )
      secondLine = 'with %s atmosphere and %s intelligent beings\n' % (
             self._atmospheres[ self.atmosphere ], self._populations[ self.population ] )

      thirdLine = 'ruled by %s %s with %s' % ( self._laws[ self.law ],
                                               self._governments[ self.government ],
                                               self._star_ports[ self.star_port ] )
      fourthLine = ''

      bases = ''
      if self.scout_base and self.naval_base:
         bases = 'supporting scout and naval presence'
      elif self.scout_base:
         bases = 'supporting scout presence'
      elif self.naval_base:
         bases = 'supporting naval presence'
      if bases:
         fourthLine = '\n' + self.prefix + '---- ' + bases

      facility_str = ''
      if self.facilities:
         facility_str = 'with facilities for ' + ','.join( self.facilities ) 
      if facility_str:
         fourthLine = '\n' + self.prefix + '---- ' + facility_str

      return primary + firstLine + self.prefix + \
                     '---- ' + secondLine + self.prefix + \
                     '---- ' + thirdLine + fourthLine
               
   @property
   def body_type( self ):
      return 'World'

class GasGiant( World ):
   def _size( self ):
      roll = D(1)
      size = 'small'
      if roll > 3:
         size = 'large'
      self.size = size
   def _atmosphere( self ):
      return
   def _hydrography( self ):
      return

   def numberOfSatallites( self ):
      if self.size == 'small':
         roll = D(2) - 4
      else:
         roll = D(2)
      if roll < 0:
         roll = 0
      self.num_of_satallites = roll
   def generateSatallites( self ):
      for x in range( self.num_of_satallites ):
         if self.size == 'small':
            size = D(2) - 6
         else:
            size = D(2) - 4
         if size == 0:
            size = 'R'
         if size < 0:
            size = 'S'

         multiple = 1
         roll = D(2)
         if roll > 7:
            multiple = 5
         if roll == 12:
            multiple = 25
         orbitNum = self.getValidSatalliteRoll( multiple, size )

         self.orbits.append( Orbit( self, orbitNum ) )
         self.orbits[-1].occupied = True
         self.orbits[-1].body = Satallite( self, self.orbits[-1], size )

   def getPossibleMainWorlds( self ):
      possibleWorlds = []
      for o in self.orbits:
         if o.body:
            for world in o.body.getPossibleMainWorlds():
               possibleWorlds.append( world )
      return possibleWorlds

   @property
   def name( self ):
      return '%s %s' % ( self.size, self.body_type )
   @property
   def body_type( self ):
      return 'Gas Giant'
   
class Satallite( World ):
   def __init__( self, world, orbit, size ):
      """ Generate A Random Satallite of 'size' """
      self.orbits = []
      self.deviation = 0

      self.atmosphere = None
      self.hydrography = None
      self.population = None
      self.government = 0

      self.law = 0
      self.star_port = 'X'
      self.space_port = 'Y'
      self.tech = 0
      self.trade_classification = ''
      self.scout_base = False
      self.naval_base = False
      self.facilities = []

      self.world = world
      self.star = world.star
      self.orbit = orbit
      self.size = size
      self.is_main_world = False

      self._atmosphere()
      self._hydrography()
      self._population()

   def _atmosphere( self ):
      size = self.size
      if size == 'R' or size == 'S':
         size = 0
      roll = D(2) - 7 + size
      if self.world.orbit.zone == 'I':
         roll = roll - 4
      if self.world.orbit.zone == 'O':
         roll = roll - 4
      if size <= 1:
         roll = 0

      if roll < 0:
         roll = 0
      if roll > 15:
         roll = 15

      self.atmosphere = roll
      if self.world.orbit.zone == 'O':
         z = self.star.orbits[ max(self.world.orbit.number - 2, 0) ].zone
         if z == 'O' or z == 'H':
            exotic = D(2)
            if exotic == 12:
               self.atmosphere = 10

   def _hydrography( self ):
      size = self.size 
      if size == 'S' or size == 'R':
         size = 0
      roll = D(2) - 7 + size
      if self.world.orbit.zone == 'O':
         roll = roll - 2
      if self.atmosphere <= 1 or self.atmosphere >= 10:
         roll = roll - 4
      if self.world.orbit.zone == 'I':
         roll = 0
      if size == 0:
         roll = 0
      if roll < 0:
         roll = 0
      if roll > 10:
         roll = 10
      self.hydrography = roll

   def _population( self ):
      size = self.size 
      if size == 'S' or size == 'R':
         size = 0
      roll = D(2) - 2
      if self.world.orbit.zone == 'I':
         roll = roll - 5
      if self.world.orbit.zone == 'O':
         roll = roll - 4
      if size <= 4:
         roll = roll - 2
      if not self.atmosphere in [ 5, 6, 8 ]:
         roll = roll - 2
      if self.size == 'R':
         roll = 0
      if roll < 0:
         roll = 0
      if roll > 10:
         roll = 10
      self.population = roll

   @property
   def prefix( self ):
      body = 'g' if isinstance( self.world, GasGiant ) else 'w'
      return self.world.prefix + '{:-<4}'.format( str(self.orbit.number) + body )

   @property
   def body_type( self ):
      return 'Satallite'

def test():
   for x in range( 100 ):
      s = SolarSystem()
      s.primary_star.printBody()

def test_tech():
   test_lvls = [ x for x in range( 17 ) ]
   x = 0
   while test_lvls:
      x += 1
      s = SolarSystem()
      lvls = copy.copy( test_lvls )
      for lvl in lvls:
         if s.primary_world:
            if s.primary_world.tech == lvl:
               test_lvls.remove( lvl )
   print '*** techs found in: %d systems' % x 

def test_law():
   test_lvls = [ x for x in range( 12 ) ]
   x = 0
   while test_lvls:
      x += 1
      s = SolarSystem()
      lvls = copy.copy( test_lvls )
      for lvl in lvls:
         if s.primary_world:
            if s.primary_world.law == lvl:
               test_lvls.remove( lvl )
   print '*** laws found in: %d systems' % x


def test_star_port():
   test_lvls = [  'A','B','C','D','E','X']
   x = 0
   while test_lvls:
      x += 1
      s = SolarSystem()
      lvls = copy.copy( test_lvls )
      for lvl in lvls:
         if s.primary_world:
            if s.primary_world.star_port == lvl:
               test_lvls.remove( lvl )
   print '*** star ports found in: %d systems' % x

def test_trade():
   test_lvls = ['rich','poor','agricultural','non-agricultural','vacuum',
                'desert','water','ice-capped', 'industrial', 'non-industrial' ]
   x = 0
   while test_lvls:
      x += 1
      s = SolarSystem()
      lvls = copy.copy( test_lvls )
      for lvl in lvls:
         if s.primary_world:
            trades = s.primary_world.trade_classification.split()
            for trade in trades:
               if trade == lvl:
                  #print s.primary_world.fullName
                  test_lvls.remove( lvl )
   print '*** trade classifications found in: %d systems' % x

def test_facilities():
   test_lvls = ['military','research','colony','mining','farming']
   x = 0
   while test_lvls:
      x += 1
      s = SolarSystem()
      lvls = copy.copy( test_lvls )
      for lvl in lvls:
         worlds = s.primary_star.getPossibleMainWorlds()
         for world in worlds:
            for facility in world.facilities:
               #print world.facilities
               if facility == lvl:
                  try:
                     test_lvls.remove( lvl )
                  except Exception as e:
                     pass
   print '*** facilities found in: %d systems' % x
   
def test_world():
   print "Staring main world checks:"
   test_tech()
   test_law()
   test_star_port()
   test_trade()

def test_other_worlds():
   print "Starting other worlds checks:"
   test_facilities()

def systemNature():
   roll = D(2)
   if roll < 8:
      roll = 'solo'
   elif roll < 12:
      roll = 'binary'
   elif roll == 12:
      roll = 'trinary'
   return roll
def createStars( system_nature ):
   return PrimaryStar( system_nature )

def test_json():
   for x in range( 100 ):
      s = SolarSystem()
      data = s.primary_star.getJson()
      pprint.pprint(data)

   #with open( 'data.json', 'w' ) as outfile:
   #   json.dump( data, outfile )

if __name__ == '__main__':
   test()
   #test_world()
   #test_other_worlds()
   
   #test_json()

