__version__ = r"1.0"

class RandomNumberGenerator( object ):
    """
    Interface for a random number generator.
    """

    def __init__( self, **kwargs ):
        """
        Creates a new random number generator.
        """

        self._initialize( **kwargs )

    def _initialize( self, **kwargs ):
        """
        Hook called from the base class' __init__ function.
        This is an empty stub.
        """

        pass

    def destroy( self ):
        """
        Hook called to clean up any internal variables.
        This is an empty stub.
        """

        pass

    def getRandomInteger( self, lowerBound, upperBound ):
        """
        Function which will return a random integer in [ lowerBound, upperBound ].
        This function will raise an error as it is required to overridden by children.
        """

        raise NotImplementedError( "Method in abstract base class not implemented." )

    def getRandomItem( self, itemList ):
        """
        This function selects a random item from the item list.
        """

        return itemList[ self.getRandomInteger( 0, len( itemList ) - 1 ) ]

class StandardRandomNumberGenerator( RandomNumberGenerator ):
    """
    Wrapper around built-in random class.
    """

    def __init__( self, generatorSeed = None, **kwargs ):
        """
        Creates a new random number generator using the built-in Random class.
        """

        super( StandardRandomNumberGenerator, self ).__init__( **kwargs )

        if generatorSeed is None:
            import random
            generatorSeed = random.random()

        from random import Random
        self._prng = Random( generatorSeed )

    def getRandomInteger( self, lowerBound, upperBound ):
        """
        Function which will return a random integer in [ lowerBound, upperBound ].
        """

        return self._prng.randint( lowerBound, upperBound )
