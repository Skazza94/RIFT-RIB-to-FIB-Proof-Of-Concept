from route import Route, DEST_TYPE_PREFIX, DEST_TYPE_POS_DISAGG_PREFIX, DEST_TYPE_NEG_DISAGG_PREFIX
from rib import Rib

N_SPF = 1
S_SPF = 2

rib = Rib()

route = Route("0.0.0.0/0", N_SPF)
route.add_next_hops([('S1', DEST_TYPE_PREFIX), ('S2', DEST_TYPE_PREFIX), ('S3', DEST_TYPE_PREFIX),
                     ('S4', DEST_TYPE_PREFIX)])

rib.put_route(route)

route = Route("10.0.0.0/8", N_SPF)
route.add_next_hops([('S1', DEST_TYPE_NEG_DISAGG_PREFIX)])

rib.put_route(route)

route = Route("10.0.0.0/8", S_SPF)
route.add_next_hops([('S2', DEST_TYPE_NEG_DISAGG_PREFIX)])

rib.put_route(route)

route = Route("10.1.0.0/16", N_SPF)
route.add_next_hops([('S3', DEST_TYPE_NEG_DISAGG_PREFIX)])

rib.put_route(route)

print(rib.destinations.get('0.0.0.0/0'))
print(rib.destinations.get('10.0.0.0/8'))
print(rib.destinations.get('10.1.0.0/16'))