import os
cwd = os.getcwd()
ead = (cwd +'/extended_acls/') 
spool = (cwd +'/snat/snat_pools') 
dpool = (cwd +'/dnat/dnat_objects')

filenames = [ filename for filename in os.listdir(ead)]
source_ips = {}
dest_ips = {}
source_pool_ips = {}
dest_pool_ips= {}

wildcard_array = {
        '0.0.0.0' : '/32', '0.0.0.1' : '/31', '0.0.0.3' : '/30', '0.0.0.7' : '/29', '0.0.0.15' : '/28', '0.0.0.31' : '/27',
        '0.0.0.255' : '/24', '0.0.3.255' : '/22', '0.0.7.255' : '/21', '0.0.15.255' : '/20', '0.0.63.255' :  '/18',
        '0.255.255.255' :  '/8',   
        }
#this is to decide what to do with data
def logic_checker(entry, source_ips, dest_ips, wca):
    if 'any' in entry:
        if entry[2] == 'any':
            dest_ips.append(entry[4]+'/32')
        elif entry[4] == 'any':
            source_ips.append(entry[3]+'/32')
        else:
            print('no match ' + entry)
            pass
    elif entry[2] == 'host' and entry[4] == 'host':
        source_ips.append(entry[3]+'/32')
        dest_ips.append(entry[5]+'/32')
    elif entry[3][0:2] == '0.' and entry[5][0:2] == '0.':
        source_ips.append(entry[2]+wca[entry[3]])
        dest_ips.append(entry[4]+wca[entry[5]])
    elif entry[3][0:2] or entry[5][0:2] == '0.':
        if entry[3][0:2] == '0.':
            source_ips.append(entry[2]+wca[entry[3]])
            dest_ips.append(entry[5]+'/32')
        elif entry[5][0:2] == '0.':
            source_ips.append(entry[3]+'/32')
            dest_ips.append(entry[4]+wca[entry[5]])
        else:
            print('no match ' + entry)
            pass
    else:
        print('no match ' + entry)
        pass
    

for file in filenames:
    global source_ips
    global dest_ips
    with open(ead+file, mode='rt') as f:
        source_ips_list = []
        dest_ips_list = []
        line_entries = [line.rstrip('\n') for line in f]
        for entry in line_entries:
            entry = entry.strip(' ').split(' ')
            logic_checker(entry, source_ips_list, dest_ips_list, wildcard_array)
            unique_source = (set(source_ips_list))
            unique_dest = (set(dest_ips_list))
            unique_source_list = [unique_ip for unique_ip in unique_source]
            unique_dest_list = [unique_ip for unique_ip in unique_dest]
            source_ips[file] = unique_source_list
            dest_ips[file] = unique_dest_list


with open(spool, mode='rt') as f:
    line_entries = [line.rstrip('\n') for line in f]
    lower_higher = []
    for entry in line_entries:
        lower_higher = []
        entry = entry.strip(' ').split(' ')
        lower_higher.append(entry[4])
        lower_higher.append(entry[5])
        source_pool_ips[entry[3]] = lower_higher


with open(dpool, mode='rt') as f:
    line_entries = [line.rstrip('\n') for line in f]
    for entry in line_entries:
        entry = entry.strip(' ').split(' ')
        if entry[5] == 'udp' or entry[5] == 'tcp':
            dest_pool_ips[entry[6]+'_'+entry[8]] = [entry[6],entry[8],entry[7],entry[9], entry[5] ]
        else:
            dest_pool_ips[entry[5]+'_'+entry[6]] = [entry[5],entry[6],'0-65535','0-65535', '']

