import getpass
import FortigateApi
ip = input('enter IP: ')
vdom = input('Enter VDOM: ')
user = input('Enter Username: ')
passwd = getpass.getpass('Enter password: ')


f = FortigateApi.Fortigate(ip, vdom, user, passwd)

source_ip_keys = [i for i in source_ips.keys()]

for i in source_ip_keys:
    for entry in source_ips[i]:
        f.AddFwAddress(name=entry, subnet=entry)

for i in source_ip_keys:
    if len(source_ips[i]) > 0:
        f.AddFwAddressGroup(name=(i+'-source'), member_list=source_ips[i])
    else:
        pass


dest_ip_keys = [i for i in dest_ips.keys()]
for i in dest_ip_keys:
    for entry in dest_ips[i]:
        f.AddFwAddress(entry, entry)

for i in dest_ip_keys:
    if len(dest_ips[i]) > 0:
        f.AddFwAddressGroup(name=(i+'-dest'), member_list=dest_ips[i])
    else:
        pass

#build source pool keys to iterate
source_pool_keys = [i for i in source_pool_ips.keys()]
#build fwip snat pools
for i in source_pool_keys:
    f.AddFwIPpool(i, source_pool_ips[i][0], source_pool_ips[i][1])

#build dest pool keys to iterate
dest_pool_keys = [i for i in dest_pool_ips.keys()]
#build fw ip dnat vips
for i in dest_pool_keys:
    if dest_pool_ips[i][4] == '':
        f.AddFwVIP(i, extip=dest_pool_ips[i][1], extintf='any', mappedip=dest_pool_ips[i][0], portforward='disable', protocol='', extport='0-65535', mappedport='0-65535', comment='')
    elif dest_pool_ips[i][4] == 'tcp' or dest_pool_ips[i][4] == 'udp':
        f.AddFwVIP(i, extip=dest_pool_ips[i][1], extintf='any', mappedip=dest_pool_ips[i][0], portforward='enable', protocol=dest_pool_ips[i][4], extport=dest_pool_ips[i][3], mappedport=dest_pool_ips[i][2], comment='')
    else:
        pass

services_tcp = []
services_udp = []
#build services to create service objects
for i in dest_pool_keys:
    if dest_pool_ips[i][4] == 'tcp':
        services_tcp.append(dest_pool_ips[i][3])
    elif dest_pool_ips[i][4] == 'udp':
        services_udp.append(dest_pool_ips[i][3])
    else:
        pass
 

for i in services_tcp:
    f.AddFwService(name=(i+'-TCP'), tcp_portrange=i, udp_portrange='', protocol='TCP/UDP/SCTP', fqdn='', iprange='0.0.0.0',  comment='')
for i in services_udp:
    f.AddFwService(name=(i+'-UDP'), tcp_portrange=i, udp_portrange='', protocol='TCP/UDP/SCTP', fqdn='', iprange='0.0.0.0',  comment='')
        
#ADD FW POLICES FOR INSIDE ZONE TO OUTSIDE ZONE USING SOURCENAT OBJECTS
for i in source_ip_keys:
    f.AddFwPolicy(srcintf='INSIDE_ZONE', dstintf='OUTSIDE_ZONE', srcaddr=(i+'-source'), dstaddr=(i+'-dest'), service='ALL', action='accept', schedule='always', nat='enable', poolname=i, ippool='enable', status='enable', comments='', traffic_shaper='', traffic_shaper_reverse='')
#f.AddFwAddressgroup(, ip_addrs)
for i in dest_pool_keys:
    if dest_pool_ips[i][4] == 'tcp' or dest_pool_ips[i][4] == 'udp':
        f.AddFwPolicy(srcintf='OUTSIDE_ZONE', dstintf='INSIDE_ZONE', srcaddr='all', dstaddr=i, service=(dest_pool_ips[i][3]+'-'+dest_pool_ips[i][4].upper()), action='accept', schedule='always', nat='disable', poolname=i, ippool=[], status='enable', comments='', traffic_shaper='', traffic_shaper_reverse='')
        pass
    else:
        f.AddFwPolicy(srcintf='OUTSIDE_ZONE', dstintf='INSIDE_ZONE', srcaddr='all', dstaddr=i, service='ALL', action='accept', schedule='always', nat='disable', poolname=i, ippool=[], status='enable', comments='', traffic_shaper='', traffic_shaper_reverse='')

