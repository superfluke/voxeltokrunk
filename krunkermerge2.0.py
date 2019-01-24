import json
import time

print_merged_pos = False
    
#binary search for obj index matching pos. Returns -1 if no obj exists at pos
def bsearch_obj_index(objs, pos):
    min =0
    max = len(objs)-1
    guess_index = int(max/2)
    guess_pos = objs[guess_index]['p']
    while(guess_pos != pos):
        if(guess_pos[1] > pos[1]):
            max = guess_index - 1
        elif(guess_pos[1] < pos[1]):
            min = guess_index + 1
        elif(guess_pos[2] > pos[2]):
            max = guess_index - 1
        elif(guess_pos[2] < pos[2]):
            min = guess_index + 1
        elif(guess_pos[0] > pos[0]):
            max = guess_index - 1
        elif(guess_pos[0] < pos[0]):
            min = guess_index + 1
        
        if(max < min):
            return -1
        
        guess_index = int((min+max)/2)
        guess_pos = objs[guess_index]['p']
    
    return guess_index

"""
#moves objects so map corner is at 0,0,0 and extends in the positive x,y,z directions
def shift_map_to_origin(objs):
    minX = minY = minZ = 999999
    for n in range(len(objs)):
        pos = objs[n]['p']
        if(pos[0] < minX):
            minX = pos[0]
        if(pos[1] < minY):
            minY = pos[1]
        if(pos[2] < minZ):
            minZ = pos[2]
            
    for n in range(len(objs)):
        objs[n]['p'][0] = objs[n]['p'][0] - minX
        #objs[n]['p'][1] = objs[n]['p'][1] - minY
        objs[n]['p'][2] = objs[n]['p'][2] - minZ
        
    return objs
"""

#convert all size/positions to work like the y axis does. position defines the starting point and size extends in a single direction
def convert_to_sane_pos_system(objs):
    for n in range(len(objs)):
        pos = objs[n]['p']
        size = objs[n]['s']
        objs[n]['p'][0] = pos[0] - ((size[0]-1) / 2)
        objs[n]['p'][2] = pos[2] - ((size[2]-1) / 2)
        
    return objs

def convert_back_to_shitty_krunker_system(objs):
    for n in range(len(objs)):
        pos = objs[n]['p']
        size = objs[n]['s']
        objs[n]['p'][0] = int(pos[0] + ((size[0]-1) / 2))
        objs[n]['p'][2] = int(pos[2] + ((size[2]-1) / 2))
        
    return objs

def print_shitty_krunker_system(obj):
    pos = obj['p']
    size = obj['s']
    print([int(pos[0] + ((size[0]-1) / 2)), obj['p'][1], int(pos[2] + ((size[2]-1) / 2))])


def are_both_odd(num1, num2):
    return num1 % 2 == 1 and num2 % 2 == 1

#returns true if the color/emissive/texture/etc of 2 objects match
def does_extra_obj_info_match(obj, obj2):
    if 't' in obj2:
        texture2 = obj2['t']
    else:
        texture2 = -1
    if 't' in obj:
        texture = obj['t']
    else:
        texture = -1

    if 'c' in obj2:
        color2 = obj2['c']
    else:
        color2 = -1
    if 'c' in obj:
        color = obj['c']
    else:
        color = -1

    if 'e' in obj2:
        emissive2 = obj2['e']
    else:
        emissive2 = -1
    if 'e' in obj:
        emissive = obj['e']
    else:
        emissive = -1
        
    if 'o' in obj2:
        opacity2 = obj2['o']
    else:
        opacity2 = -1
    if 'o' in obj:
        opacity = obj['o']
    else:
        opacity = -1
        
    if 'col' in obj2:
        collidable2 = obj2['col']
    else:
        collidable2 = -1
    if 'col' in obj:
        collidable = obj['col']
    else:
        collidable = -1
        
    if 'pe' in obj2:
        penetrate2 = obj2['pe']
    else:
        penetrate2 = -1
    if 'pe' in obj:
        penetrate = obj['pe']
    else:
        penetrate = -1
        
    if 'col' in obj2:
        collidable2 = obj2['col']
    else:
        collidable2 = -1
    if 'col' in obj:
        collidable = obj['col']
    else:
        collidable = -1
        
    if 'hp' in obj2:
        hp2 = obj2['hp']
    else:
        hp2 = -1
    if 'hp' in obj:
        hp = obj['hp']
    else:
        hp = -1
            
    return texture == texture2 and color == color2 and emissive == emissive2 and opacity == opacity2 and collidable == collidable2 and penetrate == penetrate2 and hp == hp2
    

def merge_objs(objs, start_time):
    global print_merged_pos
    
    print('Merging Y layer')
    while True:
        objs_merged = 0
        for obj in objs: 
            obj2_index = bsearch_obj_index(objs, [obj['p'][0], obj['p'][1] + obj['s'][1], obj['p'][2]])
            if(obj2_index != -1):
                obj2 = objs[obj2_index]
                if ('id' in obj or 'id' in obj2):
                    break

                if(obj2['s'][0] == obj['s'][0] and obj2['s'][2] == obj['s'][2] and does_extra_obj_info_match(obj, obj2)):
                    obj['s'][1] += objs[obj2_index]['s'][1]
                    objs.pop(obj2_index)
                    objs_merged += 1
                    if(print_merged_pos):
                        print_shitty_krunker_system(obj)
        if(objs_merged == 0):
            break
        print('    {} objects merged'.format(objs_merged))
    ytime = time.time()
    print('Finished Y merge in {} seconds'.format(round(ytime - start_time, 3)))
    
    print('Merging Z layer')
    while True:
        objs_merged = 0
        for obj in objs: 
            obj2_index = bsearch_obj_index(objs, [obj['p'][0], obj['p'][1], obj['p'][2] + obj['s'][2]])
            if(obj2_index != -1):
                obj2 = objs[obj2_index]
                if ('id' in obj or 'id' in obj2):
                    break

                if(obj2['s'][0] == obj['s'][0] and obj2['s'][1] == obj['s'][1] and does_extra_obj_info_match(obj, obj2)):
                    
                    #2 odd sized blocks do not merge nicely :(
                    if(not are_both_odd(obj['s'][2],objs[obj2_index]['s'][2])):
                        obj['s'][2] += objs[obj2_index]['s'][2]
                        objs.pop(obj2_index)
                        objs_merged += 1
                        if(print_merged_pos):
                            print_shitty_krunker_system(obj)
                   
                    #try and merge odd blocks as triplets
                    else:
                        obj3_index = bsearch_obj_index(objs, [obj2['p'][0], obj2['p'][1], obj2['p'][2] + obj2['s'][2]])
                        if(obj3_index != -1):
                            obj3 = objs[obj3_index]
                            if ('id' in obj or 'id' in obj2):
                                break
                            if(obj3['s'][0] == obj2['s'][0] and obj3['s'][1] == obj2['s'][1] and does_extra_obj_info_match(obj3, obj2)):
                                obj['s'][2] += objs[obj2_index]['s'][2] + objs[obj3_index]['s'][2]
                                objs.pop(obj2_index)
                                obj3_index = bsearch_obj_index(objs, [obj3['p'][0], obj3['p'][1], obj3['p'][2]])
                                objs.pop(obj3_index)
                                objs_merged += 2
                                if(print_merged_pos):
                                    print_shitty_krunker_system(obj)
        if(objs_merged == 0):
            break
        
        print('    {} objects merged'.format(objs_merged))
    ztime = time.time()
    print('Finished Z merge in {} seconds'.format(round(ztime - ytime, 3)))
    
    print('Merging X layer')
    while True:
        objs_merged = 0
        for obj in objs: 
            obj2_index = bsearch_obj_index(objs, [obj['p'][0] + obj['s'][0], obj['p'][1], obj['p'][2]])
            if(obj2_index != -1):
                obj2 = objs[obj2_index]
                if ('id' in obj or 'id' in obj2):
                    break

                if(obj2['s'][2] == obj['s'][2] and obj2['s'][1] == obj['s'][1] and does_extra_obj_info_match(obj, obj2)):
                   
                    #2 odd sized blocks do not merge nicely :(
                    if(not are_both_odd(obj['s'][2],objs[obj2_index]['s'][2])):
                        obj['s'][0] += objs[obj2_index]['s'][0]
                        objs.pop(obj2_index)
                        objs_merged += 1
                        if(print_merged_pos):
                            print_shitty_krunker_system(obj)
                        
                    #try and merge odd blocks as triplets
                    else:
                        obj3_index = bsearch_obj_index(objs, [obj2['p'][0] + obj2['s'][0], obj2['p'][1], obj2['p'][2]])
                        if(obj3_index != -1):
                            obj3 = objs[obj3_index]
                            if ('id' in obj or 'id' in obj2):
                                break
                            if(obj3['s'][2] == obj2['s'][2] and obj3['s'][1] == obj2['s'][1] and does_extra_obj_info_match(obj3, obj2)):
                                obj['s'][0] += objs[obj2_index]['s'][0] + objs[obj3_index]['s'][0]
                                objs.pop(obj2_index)
                                obj3_index = bsearch_obj_index(objs, [obj3['p'][0], obj3['p'][1], obj3['p'][2]])
                                objs.pop(obj3_index)
                                objs_merged += 2
                                if(print_merged_pos):
                                    print_shitty_krunker_system(obj)
        if(objs_merged == 0):
            break
        print('    {} objects merged'.format(objs_merged))
    xtime = time.time()
    print('Finished X merge in {} seconds'.format(round(xtime - ztime, 3)))
    
    return objs
    
infile = 'map.txt'
outfile = 'mergedmap.txt'
start_time = time.time()

with open(infile, 'r') as ifile:
    mapin = json.load(ifile)
    mapout = mapin
    print('File {} loaded with {} objects'.format(infile, len(mapin['objects'])+1))
    objs = mapin['objects']

#objs = shift_map_to_origin(objs)
objs = convert_to_sane_pos_system(objs)
#objs = shift_map_to_origin(objs)

#sort objects to utilize faster binary search
obj_sorted = sorted(objs, key=lambda k: (k['p'][1], k['p'][2], k['p'][0]))
obj_sorted = merge_objs(obj_sorted, start_time)
obj_sorted = convert_back_to_shitty_krunker_system(obj_sorted)
mapout['objects'] = obj_sorted

with open(outfile, 'w') as ofile:
    json.dump(mapout, ofile)

print('Total merge time {} seconds'.format(round(time.time() - start_time, 3)))
print('Finished with {} objects'.format(len(mapout['objects'])+1))
print('Saved to {}'.format(outfile))