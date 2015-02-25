"""Contains the Enum class for symbolically representing code constants"""
import inspect
import random

class MetaEnum(type):
    """MetaClass for Enum"""
    def __init__(mcs, name, bases, attrs):
        type.__init__(mcs, name, bases, attrs)

        item_dict = {}

        for base in bases:
            if hasattr(base, '_item_dict'):
                for k,v in base._item_dict.items():
                    if not issubclass(mcs, NonUniqueEnum) and k in item_dict and (item_dict[k].key != v.key or item_dict[k].value != v.value):
                        raise Exception('Value already exists.  Found %s for %s.  Trying to add %s for %s' % (item_dict[k], k, v, k))

                item_dict.update(base._item_dict)

        if name == 'Enum':
            enums = []
        elif 'enums' in attrs:
            underscore_check = False
            enums = attrs['enums'].items()
        else:
            underscore_check = True
            enums = attrs.items()

        for name, val in enums:
            if underscore_check and name.startswith('_') or inspect.isroutine(val):
                continue

            if isinstance(val, EnumItem):
                item = val
            elif hasattr(val, '__iter__'):
                item = EnumItem(val[0], val[1], sort=val[0])
                if len(val) > 2:
                    item.metadata = val[2]
            else:
                item = EnumItem(val, name)

            item.name = name

            setattr(mcs, name, item.key)
            if not issubclass(mcs, NonUniqueEnum) and item.key in item_dict and item_dict[item.key] != name:
                raise Exception('Value already exists.  Found %s for %s.  Trying to add %s for %s' % (item_dict[item.key], item.key, name, item.key))
            item_dict[item.key] = item

        mcs._item_dict = item_dict

    def __getitem__(mcs, key):
        item = mcs._item_dict.__getitem__(key)
        if item:
            return item.value
        return None

    def __iter__(mcs):
        for key in mcs._item_dict:
            yield key

    def __repr__(mcs):
        return '{}.{}'.format(mcs.__module__, mcs.__name__)

class EnumItem(object):
    def __init__(self, key, value, name=None, sort=None, **metadata):
        self.key = key
        self.value = value
        self.name = name
        self.sort = sort
        self.metadata = metadata

class Enum:
    """Enum Data Type

    Testing a normal enum:
    >>> class TestEnumA(Enum):
    ...     A = 1
    ...     B = (2, u'b')
    ...     C = (3, u'c', u'cmeta')
    ...     _Z = (100, u'z')
    ...
    >>> TestEnumA.A
    1
    >>> TestEnumA.B
    2
    >>> TestEnumA._Z
    (100, u'z')
    >>> TestEnumA.lookup(TestEnumA.C)
    'C'
    >>> TestEnumA.verbose(TestEnumA.C)
    u'c'
    >>> TestEnumA.metadata(TestEnumA.A)
    >>> TestEnumA.metadata(TestEnumA.C)
    u'cmeta'
    >>> TestEnumA.metadata(100, 'default')
    'default'
    >>> TestEnumA[TestEnumA.C] == TestEnumA.verbose(TestEnumA.C)
    True
    >>> TestEnumA.verbose(100)
    ''
    >>> TestEnumA[100]
    Traceback (most recent call last):
    ...
    KeyError: 100
    >>> TestEnumA.get(100)
    >>> TestEnumA.get(100, 'Z')
    'Z'
    >>> TestEnumA.items()
    [(1, 'A'), (2, 'B'), (3, 'C')]
    >>> TestEnumA.keys()
    [1, 2, 3]
    >>> TestEnumA.values()
    ['A', 'B', 'C']
    >>> TestEnumA.verbose()
    [(1, 'A'), (2, u'b'), (3, u'c')]
    >>> for k in TestEnumA:
    ...     print k
    ...
    1
    2
    3

    Testing an inherited enum:
    >>> class TestEnumB(TestEnumA):
    ...     D = 5
    ...
    >>> TestEnumB.A
    1
    >>> TestEnumB.D
    5
    >>> TestEnumB.verbose(TestEnumB.C)
    u'c'
    >>> TestEnumB[TestEnumB.C] == TestEnumB.verbose(TestEnumB.C)
    True
    >>> TestEnumB.items()
    [(1, 'A'), (2, 'B'), (3, 'C'), (5, 'D')]
    >>> TestEnumB.keys()
    [1, 2, 3, 5]
    >>> TestEnumB.values()
    ['A', 'B', 'C', 'D']
    >>> TestEnumB.verbose()
    [(1, 'A'), (2, u'b'), (3, u'c'), (5, 'D')]
    >>> for k in TestEnumB:
    ...     print k
    ...
    1
    2
    3
    5

    Testing a mixed enum:
    >>> class TestEnumC(Enum):
    ...     E = 0
    ...
    >>> class TestEnumD(TestEnumA, TestEnumC):
    ...     pass
    ...
    >>> TestEnumD.A
    1
    >>> TestEnumD.E
    0
    >>> TestEnumD.verbose(TestEnumA.C)
    u'c'
    >>> TestEnumD[TestEnumA.C] == TestEnumD.verbose(TestEnumA.C)
    True
    >>> TestEnumD.items()
    [(0, 'E'), (1, 'A'), (2, 'B'), (3, 'C')]
    >>> TestEnumD.keys()
    [0, 1, 2, 3]
    >>> TestEnumD.values()
    ['E', 'A', 'B', 'C']
    >>> TestEnumD.verbose()
    [(0, 'E'), (1, 'A'), (2, u'b'), (3, u'c')]

    Testing old-style enums with mixins:
    >>> class TestEnumE(TestEnumA):
    ...     enums = { 'F': (0, u'f') }
    ...
    >>> TestEnumE.A
    1
    >>> TestEnumE.F
    0
    >>> TestEnumE.verbose(TestEnumE.C)
    u'c'
    >>> TestEnumE[TestEnumE.C] == TestEnumE.verbose(TestEnumE.C)
    True
    >>> TestEnumE.items()
    [(0, 'F'), (1, 'A'), (2, 'B'), (3, 'C')]
    >>> TestEnumE.keys()
    [0, 1, 2, 3]
    >>> TestEnumE.values()
    ['F', 'A', 'B', 'C']
    >>> TestEnumE.verbose()
    [(0, u'f'), (1, 'A'), (2, u'b'), (3, u'c')]
    """

    # pylint: disable-msg=E1101,W0232

    __metaclass__ = MetaEnum

    @classmethod
    def max_length(cls):
        return max([len(str(x)) for x in cls.keys()])

    @classmethod
    def to_int(cls, value):
        # pylint: disable-msg=W0703
        try:
            return int(value)
        except Exception:
            return None

    @classmethod
    def from_int(cls, value):
        return value

    @classmethod
    def random(cls):
        verbose = cls.verbose()
        length = len(verbose)
        index = random.randint(0, length - 1)

        return verbose[index][0]

    @classmethod
    def lookup(cls, key, get=False):
        """Returns the label for a given Enum key"""
        if get:
            item = cls._item_dict.get(key)
            return item.name if item else key
        return cls._item_dict[key].name

    @classmethod
    def keys(cls):
        """Returns all of the Enum keys"""
        return cls._item_dict.keys()

    @classmethod
    def values(cls):
        """Returns all of the Enum values"""
        return [x.name for x in cls._item_dict.values()]

    @classmethod
    def items(cls):
        """Returns pairs of Enum keys and values"""
        return [(x[0], x[1].name) for x in cls._item_dict.items()]

    @classmethod
    def verbose(cls, key=False, default=''):
        """Returns the verbose name for a given enum value"""
        if key is False:
            items = cls._item_dict.values()
            return [(x.key, x.value) for x in sorted(items, key=lambda x:x.sort or x.key)]

        item = cls._item_dict.get(key)
        return item.value if item else default

    @classmethod
    def get(cls, key, default=None):
        return cls.verbose(key=key, default=default)

    @classmethod
    def reverbose(cls, val, *args):
        for item in cls._item_dict.items():
            if item.value == val:
                return item.key
        if len(args) > 0:
            return args[0]
        raise KeyError(val)

    @classmethod
    def metadata(cls, *args):
        if len(args) == 0:
            return {x.key:x.metadata for x in cls._item_dict.values()}

        item = cls._item_dict.get(*args)
        if isinstance(item, EnumItem):
            return item.metadata
        return item

    @classmethod
    def next_available_key(cls):
        sorted_keys = sorted(cls.keys(), reverse=True)
        return sorted_keys[0] + 1 if sorted_keys else 0

    @classmethod
    def rest_as_json(cls, api_user, user, top_level_is_list=False, top_level_obj=None):
        ret = cls.verbose()

        for i in range(0, len(ret)):
            ret[i] = (ret[i][0], ret[i][1], cls.metadata(ret[i][0]))

        return ret

class NonUniqueEnum(Enum):
    pass
