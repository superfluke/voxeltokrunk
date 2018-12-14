import json
import time
import pdb
from operator import itemgetter

voxel_size = 10

def new_krunk_map():
    empty_map = """
    {"name":"modmap","modURL":"","ambient":9937064,"light":15923452,"sky":14477549,"fog":9280160,"fogD":900,"camPos":[0,0,0],"spawns":[],"objects":[]}
    """
    return json.loads(empty_map)

def voxel_to_krunk(voxel):
    global voxel_size

    newthing = {
       "p": [int(voxel[0])*voxel_size, int(voxel[1])*voxel_size, int(voxel[2])*voxel_size],
       "s": [voxel_size, voxel_size, voxel_size],
    }
    return newthing

def merge_krunk_obj(objs, start_time):
    global voxel_size
    
    #merge up
    print('Merging Y layer')
    while True:
        objs_merged = 0
        for obj in objs: 
            #voxel_above = get_obj_index(objs, [obj['p'][0], obj['p'][1] + obj['s'][1], obj['p'][2]])
            voxel_above = bsearch_obj_index(objs, [obj['p'][0], obj['p'][1] + obj['s'][1], obj['p'][2]])
            if(voxel_above != -1):
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
            search_pos = obj['p'][0]
            search_pos += voxel_size
            voxel_right = bsearch_obj_index(objs, [search_pos, obj['p'][1], obj['p'][2]])
            while(voxel_right != -1):
                obj_right = objs[voxel_right]
                if(obj_right['s'][1]  == obj['s'][1]): #make sure objs are same height before merging in x direction
                    obj['s'][0] += obj_right['s'][0]
                    obj['p'][0] += int(obj_right['s'][0]/2) #adjust x position to account for the increase in size
                    objs.pop(voxel_right)
                    objs_merged += 1
                else:
                    break
                 
                search_pos += voxel_size
                voxel_right = bsearch_obj_index(objs, [search_pos, obj['p'][1], obj['p'][2]])
                
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
            search_pos = obj['p'][2]
            search_pos += voxel_size
            voxel_forward = bsearch_obj_index(objs, [obj['p'][0], obj['p'][1], search_pos])
            while(voxel_forward != -1):
            #if(voxel_forward != -1):
                if(obj['p'][0] == 210 and obj['p'][2] >100 and obj['p'][1] == 50):
                    pdb.set_trace()
                    
                obj_foward = objs[voxel_forward]
                if(obj_forward['s'][1]  == obj['s'][1] and obj_forward['s'][0] == obj['s'][0]): #make sure objs are same height and width before merging in z direction
                    obj['s'][2] += obj_forward['s'][2]
                    obj['p'][2] += int(obj_forward['s'][2]/2) #adjust z position to account for the increase in size
                    objs.pop(voxel_forward)
                    objs_merged += 1
                else:
                    break
                    
                search_pos += voxel_size
                voxel_forward = bsearch_obj_index(objs, [obj['p'][0], obj['p'][1], search_pos])
                
        if(objs_merged == 0):
            break
        print('    {} objects merged'.format(objs_merged))
            
    ztime = time.time()
    print('Finished Z merge in {} seconds'.format(round(ztime - xtime, 3)))  
         
    return objs
 
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
        guess_pos = objs[guess_index][ob'p']
    
    return guess_index
    
infile = 'torus_simple.json'
outfile = 'voxelmap.txt'
obj_count = 0
start_time = time.time()

with open(infile, 'r') as ifile:
    voxels = json.load(ifile)
    mapout = new_krunk_map()
    print('File {} loaded with {} voxels'.format(infile, len(voxels['voxels'])))
    
    #sort input json by y, then z, then x
    vlist = [[int(n['x']), int(n['y']), int(n['z'])] for n in voxels['voxels']]
    vlist = sorted(vlist, key=itemgetter(1,2,0))

    for voxel in vlist:
        mapout['objects'].append(voxel_to_krunk(voxel))

mapout['objects'] = merge_krunk_obj(mapout['objects'], start_time)

with open(outfile, 'w') as ofile:
    json.dump(mapout, ofile)

print('Total merge time {} seconds'.format(round(time.time() - start_time, 3)))
print('Finished with {} objects'.format(len(mapout['objects'])))
print('Saved to {}'.format(outfile))