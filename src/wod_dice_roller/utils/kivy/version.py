import kivy

_current_version = None

# Copied from kivy.__init__.py
def parse_version( version ):
    # check for tag
    tag = None
    tagrev = None
    if '-' in version:
        l = version.split( '-' )
        if len( l ) == 2:
            version, tag = l
        elif len( l ) == 3:
            version, tag, tagrev = l
        else:
            raise Exception( 'Revision format must be X.Y.Z[-tag]' )

    # check x y z
    l = version.split( '.' )
    if len( l ) != 3:
        raise Exception( 'Revision format must be X.Y.Z[-tag]' )
    return [int( x ) for x in l], tag, tagrev

def get_version( version = None ):
   """
   Retrieves the given version as version (three item list), tag, tag revision

   If no version is given, the current kivy version is used.
   """

   if version is None:
      global _current_version

      if _current_version is None:
         version = kivy.__version__
         _current_version = VersionInformation( *parse_version( version ) )

      result = _current_version
   else:
      result = VersionInformation( *parse_version( version ) )

   return result

class VersionInformation( object ):
   def __init__( self, version, tag, tagrev ):
      self.version = version
      self.major_version, self.minor_version, self.revision = self.version
      self.tag = tag
      self.tagrev = tagrev

   def is_version( self, version, tag = None, tagrev = None ):
      result = self.version == version

      if result and tag is not None:
         result = self.tag == tag

         if result and tagrev is not None:
            result = self.tagrev == tag

      return result

   def cmp_version( self, version ):
      result = 0

      try:
         for index, value in enumerate( version ):
            if self.version[ index ] < value:
               result = -1
            elif self.version[ index ] > value:
               result = 1
      except:
         result = 1

      return result

   def lt_version( self, version ):
      return self.cmp_version( version ) == -1

   def lte_version( self, version ):
      return not self.gt_version( version )

   def eq_version( self, version ):
      return self.cmp_version( version ) == 0

   def ne_version( self, version ):
      return not self.eq_version( version )

   def gt_version( self, version ):
      return self.cmp_version( version ) == 1

   def gte_version( self, version ):
      return not self.lt_version( version )
