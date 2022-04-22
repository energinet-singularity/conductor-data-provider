import pandas as pd
import logging

log = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


# TODO make acline class
# TODO make aclinesegment class

"""
obj1 = ACLineSegment(mrid='a1')
obj2 = ACLineSegment(mrid='b2', parm1=2)
#print(obj1.mrid)
objs = [obj1, obj2]
#print(getattr(test, 'mrid'))


dataframe = pd.DataFrame([o.__dict__ for o in objs])
print(dataframe)

data = [{attr: getattr(p,attr) for attr in dir(p) if not attr.startswith('_')} for p in objs]
df = pd.DataFrame(data)
print(df)
"""


"""
class DumbClass:
    def __init__(self, p):
        self._ciao = p

    @property
    # description = property(operator.attrgetter('_description'))
    def ciao(self):
        return self._ciao

    @ciao.setter
    def ciao(self, v):
        log.info('set using settet')
        self._ciao = v
d = DumbClass("hi")
print(d.ciao)

d.ciao = 'bye'
print(d.ciao)
"""
