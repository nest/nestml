#ifndef _MATHS_UTIL_
#define _MATHS_UTIL_

#define FLOATING_POINT

typedef unsigned int Card;

#define START 0

#ifdef FLOATING_POINT

#include <math.h>

typedef float          REAL;
typedef float          UREAL;
typedef float          FRACT;
typedef float          UFRACT;
#define REAL_CONST(x)   x
#define UREAL_CONST(x)  x
#define FRACT_CONST(x)  x
#define UFRACT_CONST(x) x


#define ONE             1.00000000000000000
#define HALF            0.50000000000000000
#define ZERO            0.00000000000000000

#define POW( x, p )     pow( (x), (p) )

#define SQRT( x )       sqrt( x )
#define EXP( x )        exp( x )
#define LN( x )         log( x )
#define ABS( x )        fabs(x)


#define MAX( x, y )     MAX_HR(  (x), (y) )
#define SIGN( x, y )    ( (macro_arg_1=(y)) >= ZERO ? ABS( x ) : -ABS( x ) )

#define ACS_DBL_TINY    1.0e-300

#else   

#include <stdfix.h>
#define REAL_CONST(x)   x##k	 
#define UREAL_CONST(x)  x##uk    
#define FRACT_CONST(x)  x##lr
#define UFRACT_CONST(x) x##ulr

#define ONE             REAL_CONST(1.0000)
#define HALF            REAL_CONST(0.5000)
#define ZERO            REAL_CONST(0.0000)
#define ACS_DBL_TINY    REAL_CONST(0.000001)

#define ABS( x )        absfx( x )

#define SIGN( x, y )    ( (macro_arg_1=(y)) >= ZERO ? ABS( x ) : -ABS( x ) )

#endif

#ifdef FLOATING_POINT

#define REAL_COMPARE( x, op, y ) ( (x) op (y) )
#define REAL_TWICE( x ) ((x) * 2.00000 )
#define REAL_HALF( x )  ((x) * 0.50000 )

#else

#define REAL_COMPARE( x, op, y ) ( bitsk( (x) ) op  bitsk( (y) ) )
#define REAL_TWICE( x )  ((x) * 2.000000k ) 
#define REAL_HALF( x )   ((x) * 0.500000k ) 

#endif

#define MIN_HR(a, b) ({\
    __type_of__(a) _a = (a); \
    __type_of__(b) _b = (b); \
    _a <= _b? _a : _b;})

#define MAX_HR(a, b) ({\
    __type_of__(a) _a = (a); \
    __type_of__(b) _b = (b); \
    _a > _b? _a : _b;})

#define SQR(a) ({\
    __type_of__(a) _a = (a); \
    _a == ZERO? ZERO: _a * _a;})

#define CUBE(a) ({\
    __type_of__(a) _a = (a); \
    _a == ZERO? ZERO: _a * _a * _a;})

#endif  // _MATHS_UTIL_

