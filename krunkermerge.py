import json
import time
from operator import itemgetter

voxel_size = 10
verbose_logging = False

def new_krunk_map():
    empty_map = """
    {"name":"modmap","modURL":"","ambient":9937064,"light":15923452,"sky":14477549,"fog":9280160,"fogD":900,"camPos":[0,0,0],"spawns":[],"objects":[]}
    """
    return json.loads(empty_map)

#returns index of object given a position, returns -1 if object does not exist
def get_obj_index(objs, pos):
    for x in range(len(objs)):
        if(objs[x]['p'] == pos):
            return x
    return -1
    
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

#binary search for closest touching obj index to focus_obj. Returns -1 if no obj exists 
def bsearch_closest_touching_obj_index(objs, focus_obj, axis):
    min =0
    max = len(objs)-1
    guess_index = int(max/2)
    guess_pos = objs[guess_index]['p']
    pos = focus_obj['p']
    
    if(axis == 'x'):
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
                break
                
            guess_index = int((min+max)/2)
            guess_pos = objs[guess_index]['p']
                
    elif(axis == 'z'):
        while(guess_pos != pos):
            if(guess_pos[1] > pos[1]):
                max = guess_index - 1
            elif(guess_pos[1] < pos[1]):
                min = guess_index + 1
            elif(guess_pos[0] > pos[0]):
                max = guess_index - 1
            elif(guess_pos[0] < pos[0]):
                min = guess_index + 1
            elif(guess_pos[2] > pos[2]):
                max = guess_index - 1
            elif(guess_pos[2] < pos[2]):
                min = guess_index + 1
                
            if(max < min):
                break
                
            guess_index = int((min+max)/2)
            guess_pos = objs[guess_index]['p']
    
    if(guess_pos == pos):
        min = guess_index
        max = guess_index

    objs_to_test = [max, min]
    if(min + 1 < len(objs)):
        objs_to_test.append(min+1)
    if(max - 1 >= 0):
        objs_to_test.append(max-1)

    for index in objs_to_test:
        test_obj = objs[index]
        if(test_obj != focus_obj):
            if(axis == 'x'):
                print(test_obj['p'])
                print(focus_obj['p'])
            if(are_objs_touching(focus_obj, test_obj, axis)):
                return index

    return -1
    
#returns true if objs are both touching on the input axis and same size on other axises (axi?) (axes?)
def are_objs_touching(obj1, obj2, axis):
    if(obj1['s'][1] != obj2['s'][1]):
        return False
        
    if(axis == 'x'):
        if(obj1['s'][2] != obj2['s'][2] or obj1['p'][2] != obj2['p'][2]):
            return False
        pos1 = obj1['p'][0]
        pos2 = obj2['p'][0]
        size1 = obj1['s'][0]
        size2 = obj2['s'][0]
    elif(axis == 'z'):
        if(obj1['s'][0] != obj2['s'][0] or obj1['p'][0] != obj2['p'][0]):
            return False
        pos1 = obj1['p'][2]
        pos2 = obj2['p'][2]
        size1 = obj1['s'][2]
        size2 = obj2['s'][2]
        
    if(pos2 < pos1):
        tempp = pos1
        temps = size1
        pos1 = pos2
        size1 = size2
        pos2 = tempp
        size2 = temps
        
    endpt1 = pos1 + int((size1 + 0.5) / 2.0)
    endpt2 = pos2 - int(size2 / 2.0)
    
    return endpt1 == endpt2
    

def voxel_to_krunk(voxel):
    global voxel_size

    newthing = {
       "p": [int(voxel[0])*voxel_size, int(voxel[1])*voxel_size, int(voxel[2])*voxel_size],
       "s": [voxel_size, voxel_size, voxel_size],
    }
    return newthing

def merge_krunk_obj(objs, start_time):
    global verbose_logging
    
    #merge up
    print('Merging Y layer')
    while True:
        objs_merged = 0
        for obj in objs: 
            #voxel_above = get_obj_index(objs, [obj['p'][0], obj['p'][1] + obj['s'][1], obj['p'][2]])
            voxel_above = bsearch_obj_index(objs, [obj['p'][0], obj['p'][1] + obj['s'][1], obj['p'][2]])
            if(voxel_above != -1):
                obj_above = objs[voxel_above]
                if ('id' in obj or 'id' in obj_above):
                    break

                if 't' in obj_above:
                    texture_above = obj_above['t']
                else:
                    texture_above = -1
                if 't' in obj:
                    texture = obj['t']
                else:
                    texture = -1

                if 'c' in obj_above:
                    color_above = obj_above['c']
                else:
                    color_above = -1
                if 'c' in obj:
                    color = obj['c']
                else:
                    color = -1

                if 'e' in obj_above:
                    emissive_above = obj_above['e']
                else:
                    emissive_above = -1
                if 'e' in obj:
                    emissive = obj['e']
                else:
                    emissive = -1

                if(obj_above['s'][0] == obj['s'][0] and obj_above['s'][2] == obj['s'][2] and texture == texture_above and color == color_above and emissive == emissive_above):
                    if(verbose_logging):
                        print(objs[voxel_above]['p'])
                    obj['s'][1] += objs[voxel_above]['s'][1]
                    objs.pop(voxel_above)
                    objs_merged += 1
        if(objs_merged == 0):
            break
        print('    {} objects merged'.format(objs_merged))
    ytime = time.time()
    print('Finished Y merge in {} seconds'.format(round(ytime - start_time, 3)))
    
    #merge x direction
    print('Merging X layer')
    while True:
        objs_merged = 0
        for obj in objs: 
            #voxel_right = get_obj_index(objs, [obj['p'][0] + obj['s'][0], obj['p'][1], obj['p'][2]])
            #voxel_right = bsearch_obj_index(objs, [obj['p'][0] + obj['s'][0], obj['p'][1], obj['p'][2]])
            voxel_right = bsearch_closest_touching_obj_index(objs, obj, 'x')
            if(voxel_right != -1):
                obj_right = objs[voxel_right]
                if ('id' in obj or 'id' in obj_right):
                    break

                if 't' in obj_right:
                    texture_right = obj_right['t']
                else:
                    texture_right = -1
                if 't' in obj:
                    texture = obj['t']
                else:
                    texture = -1

                if 'c' in obj_right:
                    color_right = obj_right['c']
                else:
                    color_right = -1
                if 'c' in obj:
                    color = obj['c']
                else:
                    color = -1

                if 'e' in obj_right:
                    emissive_right = obj_right['e']
                else:
                    emissive_right = -1
                if 'e' in obj:
                    emissive = obj['e']
                else:
                    emissive = -1 

                if(obj_right['s'][1]  == obj['s'][1] and obj_right['s'][2] == obj['s'][2] and texture == texture_right and color == color_right and emissive == emissive_right):
                    if(verbose_logging):
                        print(obj_right['p'])
                    obj['s'][0] += obj_right['s'][0]
                    obj['p'][0] += int(obj_right['s'][0]/2) #adjust x position to account for the increase in size
                    objs.pop(voxel_right)
                    objs_merged += 1
        if(objs_merged == 0):
            break
        print('    {} objects merged'.format(objs_merged))
            
    xtime = time.time()
    print('Finished X merge in {} seconds'.format(round(xtime - ytime, 3)))
 
    #merge z direction
    print('Merging Z layer')
    while True:
        objs_merged = 0
        for obj in objs: 
            #voxel_forward = get_obj_index(objs, [obj['p'][0], obj['p'][1], obj['p'][2] + obj['s'][2]])
            voxel_forward = bsearch_obj_index(objs, [obj['p'][0], obj['p'][1], obj['p'][2] + obj['s'][2]])
            if(voxel_forward != -1):
                obj_forward = objs[voxel_forward]
                if ('id' in obj or 'id' in obj_forward):
                    break

                if 't' in obj_forward:
                    texture_forward = obj_forward['t']
                else:
                    texture_forward = -1
                if 't' in obj:
                    texture = obj['t']
                else:
                    texture = -1

                if 'c' in obj_forward:
                    color_forward = obj_forward['c']
                else:
                    color_forward = -1
                if 'c' in obj:
                    color = obj['c']
                else:
                    color = -1

                if 'e' in obj_forward:
                    emissive_forward = obj_forward['e']
                else:
                    emissive_forward = -1
                if 'e' in obj:
                    emissive = obj['e']
                else:
                    emissive = -1  

                if(obj_forward['s'][1]  == obj['s'][1] and obj_forward['s'][0] == obj['s'][0] and texture == texture_forward and color == color_forward and emissive == emissive_forward):
                    if(verbose_logging):
                        print(obj_forward['p'])
                    obj['s'][2] += obj_forward['s'][2]
                    obj['p'][2] += int(obj_forward['s'][2]/2) #adjust z position to account for the increase in size
                    objs.pop(voxel_forward)
                    objs_merged += 1
        if(objs_merged == 0):
            break
        print('    {} objects merged'.format(objs_merged))
            
    ztime = time.time()
    print('Finished Z merge in {} seconds'.format(round(ztime - xtime, 3)))  
         
    return objs
    
infile = 'ring10.txt'
outfile = 'mergemap.txt'
start_time = time.time()

with open(infile, 'r') as ifile:
    mapin = json.load(ifile)
    mapout = mapin#new_krunk_map()
    print('File {} loaded with {} objects'.format(infile, len(mapin['objects'])+1))
    
    #sort objects to utilize faster binary search
    #obj_sorted = mapin['objects']
    obj_sorted = sorted(mapin['objects'], key=lambda k: (k['p'][1], k['p'][2], k['p'][0]))

mapout['objects'] = merge_krunk_obj(obj_sorted, start_time)

with open(outfile, 'w') as ofile:
    json.dump(mapout, ofile)

print('Total merge time {} seconds'.format(round(time.time() - start_time, 3)))
print('Finished with {} objects'.format(len(mapout['objects'])+1))
print('Saved to {}'.format(outfile))