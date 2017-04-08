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

      self.generateSystemRequirements( self.Stars, self.Planets,
                                       self.NaturalFeatures, 
                                       self.TechFeatures,
                                       self.InfraFeatures )

      self.createStars( self.args.stars, self.args.star_type,
                        self.args.habitability_level,
                        self.args.danger_level )

      #self.createPlanets( faction, numOfPlanets, maxDangerLevel )

      #self.createNaturalFeatures( numOfNaturalFeatures, maxDangerLevel )
      #self.createTechnologicalFeatures( faction, maxTechLevel, maxDangerLevel )
      #self.createInfrastructure( faction, maxInfrastructureLevel )

   def generateSystemRequirements( self, Stars, Planets, NaturalFeatures, 
                                   TechFeatures, InfraFeatures ):
      """ Accept input objects that the system must satisfy the requirements of """
      for i,star in enumerate( Stars ):
         self.star_reqs[i].update( star.star_reqs )
      for i,planet in enumerate( Planets ):
         self.planet_reqs[i].update( planet.planet_reqs )

   def createStars( self, num_stars, star_type, habitability_level, danger_level ):
      """ Generate Star objects based off input parameters and
          any systemRequirements
      """
      for x in range( max(num_stars - len( self.Stars ),0) ):
         try:
            reqs = self.star_reqs[ x ]
         except KeyError:
            reqs = {}
         s = Star( star_type, habitability_level, danger_level, reqs )
         self.Stars.append( s )
         print "*** Generated %s" % s.name


   def createPlanets( self, factions, numOfPlanets, maxDangerLevel ):
      print 'createPlanets'

   def createNaturalFeatures( self, numOfFeatures, maxDangerLevel ):
      print 'createNaturalFeatures'

   def createTechnologicalFeatures( self, faction, maxTechLevel, maxDangerLevel ):
      print 'createTechnologicalFeatures'

   def createInfrastructure( self, faction, maxInfrastructureLevel ):
      print 'createInfrastrucute'

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
   star_types = [ 'yellow', 'red giant', 'white dwarf', 'neutron' ]
   def __init__( self, star_type, habitability_level, danger_level, star_reqs={} ):
      super( Star, self ).__init__( reqs=star_reqs )
      s = getattr( self, 'star_type', None ) or star_type
      h = getattr( self, 'habitability_level', -1 ) or habitability_level
      d = getattr( self, 'danger_level', -1 ) or danger_level
      if h < 0:
         h = 3 * random.random()
      if d < 0:
         d = 3 * random.random()
      
      if s == 'random':
         types = self.star_types
         if d >= 1.5:
            types = [ 'red giant', 'neutron' ]
         else:
            types = [ 'yellow', 'white dwarf' ]

         if h >= 2:
            if h >= 2.5:
               if 'yellow' not in types:
                  types.append( 'yellow' )
            if 'neutron' in types:
               types.remove( 'neutron' )
         index = int( random.random() * len( types ) )
         self.star_type = s = types[ index  ]

   @property
   def name( self ):
      return '%s %s' % ( self.star_type, self.body_type )
      

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
   


