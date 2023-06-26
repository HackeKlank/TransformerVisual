import bpy
import bmesh
import mathutils
import math
def oneVcter(x,y,z):
    return mathutils.Vector((x,y,z))
def translate(bm, directionVector):
    for v in bm.verts:
        translation_Matrix = mathutils.Matrix.Translation(directionVector)
        v.co = translation_Matrix @ v.co
    return
def smosh(bm, scaleVector):
    for v in bm.verts:
        scale_Matrix = mathutils.Matrix.Diagonal(scaleVector).to_4x4()
        v.co = scale_Matrix @ v.co
    return
def embodyMesh(bm):
    mesh = bpy.data.meshes.new("Mesh")
    obj = bpy.data.objects.new("Mesh", mesh)
    bpy.context.collection.objects.link(obj)
    bm.to_mesh(mesh)
    bm.free()
    return
def selectAllbp():
    bpy.ops.object.select_all(action='SELECT')
    try:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
    except IndexError:
        print("No objects in the scene.")
    return
def deselectAllbp():
    bpy.ops.object.select_all(action='DESELECT')
    return
def selectMeshbp():
    bpy.ops.mesh.select_all(action='SELECT')
    return
def deselectMeshbp():
    bpy.ops.mesh.select_all(action='DESELECT')
    return
def joinAll():
    selectAllbp()
    bpy.ops.object.join() # Merge the selected objects into one
    bpy.ops.object.mode_set(mode='EDIT') # Switch to Edit Mode
    bpy.ops.mesh.select_all(action='SELECT') # Select all vertices
    bpy.ops.mesh.remove_doubles() # Merge vertices by distance
    bpy.ops.object.mode_set(mode='OBJECT') # Switch back to Object Mode
    selectAllbp()
    return
def selectionToBmesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    return bm
def deleteAll():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
def modeObj():
    try:
        bpy.ops.object.mode_set(mode='OBJECT')  # Switch back to Object Mode
    except RuntimeError:
        return
def modeEdt():
    bpy.ops.object.mode_set(mode='EDIT')  # Switch back to Object Mode
def editView():
    modeEdt()
    deselectMeshbp()
def grid(axisVector, offsetVector, density):
    # Create bmesh and unit Cube
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.translate(bm, verts=list(bm.verts), vec=mathutils.Vector((1/2, 1/2, 1/2)))
    # Dimensionalize the cube
    smosh(bm,axisVector)
    # Make the cube equal to the density in each axis
    xCuts = math.floor(density*axisVector[0])
    yCuts = math.floor(density*axisVector[1])
    zCuts = math.floor(density*axisVector[2])
    try:
        xScale = 1 / xCuts
    except ZeroDivisionError:
        xScale = 0
    try:
        yScale = 1 / yCuts
    except ZeroDivisionError:
        yScale = 0
    try:
        zScale = 1 / zCuts
    except ZeroDivisionError:
        zScale = 0

    iterationsVector = mathutils.Vector((xCuts, yCuts, zCuts))  # Says how many iterations there are
    scaleVector = mathutils.Vector((xScale,yScale,zScale)) # Scales the vectors
    # Make them into density cubes
    smosh(bm, scaleVector)
    translate(bm,offsetVector)
    # Create the grid
    bm_now = bm
    # Move them around based on their non-zero dimensions
    for d in range(3):
        for i in range(int(iterationsVector[d])-1):
            bm_temp = bm_now.copy() # Will be an embodied copy of the placeholder mesh
            bm_copy = bm_now.copy() # Copy the mesh
            embodyMesh(bm_temp) # Embody the old mesh
            translater = mathutils.Vector((0,0,0))
            translater[d] = axisVector[d]*scaleVector[d] # Care only about the axis you want to move along
            translate(bm_copy, translater) # Translate the copy mesh
            bm_now = bm_copy # Replace the placeholder mesh with the translated copy mesh
        embodyMesh(bm_now)
        joinAll()
        bm_now = selectionToBmesh(bpy.context.active_object)
    return

def transform(transformation, time, transition, hide, Res):

    transitionConst = 0.0

    if transition:
        transitionConst = 1.0

    bpy.context.preferences.edit.use_global_undo = False  # For efficiency, get rid of global undo
    original_object = bpy.context.active_object # Get original object

    # Duplicate original object
    bpy.ops.object.duplicate({"object": original_object, "selected_objects": [original_object]})
    if hide:
        original_object.hide_viewport = True

    activeObj = bpy.context.active_object # Get the duplicated object, which will be the active object after duplication

    # Add basis shape key
    activeObj.shape_key_add(name='Basis')
    activeObj.active_shape_key_index = 1

    framesPerSecond = 24 # Blender constant
    frameDivisor = Res

    upperRange = int(math.floor(time*framesPerSecond/frameDivisor))
    for f in range(upperRange): # Accurate to the nearest one-twenty-fourths of a second
        frameIndex = f+2
        # We add two because the basis shape key starts on frame 1.
        # The for loop starts at index zero and ends one before the upperRange,
        # so we must add 2 for our first shape key to start on frame 2.
        # Add new shape key
        keyString = 'Key ' + str(frameIndex)
        activeObj.shape_key_add(name=keyString)
        activeObj.active_shape_key_index = frameIndex

        for i, v in enumerate(original_object.data.vertices):
            remainder = (upperRange-frameIndex+1)/(upperRange)
            x0,y0,z0 = v.co.x, v.co.y, v.co.z
            xr,yr,zr = x0*remainder*transitionConst, y0*remainder*transitionConst, z0*remainder*transitionConst
            x, y, z = x0*(1-remainder), y0*(1-remainder), z0*(1-remainder) # Referenced by transformations[i]
            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.x = eval(transformation[0])+xr
            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.y = eval(transformation[1])+yr
            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.z = eval(transformation[2])+zr

        activeObj.data.shape_keys.key_blocks[keyString].value = 1.0
        activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=frameIndex*frameDivisor)
        activeObj.data.shape_keys.key_blocks[keyString].value = 0.0
        activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=(frameIndex-1)*frameDivisor)
        if ((frameIndex-1) < upperRange): # Avoid adding a frame after the last shape key turns to a value of 1.0
            activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=(frameIndex+1)*frameDivisor)
    if hide: # Destroy the unchanged mesh
        bpy.data.objects.remove(original_object, do_unlink=True)
    bpy.context.preferences.edit.use_global_undo = True
def hollow(dimension, offset):
    # nudgeVector =
    obj = bpy.context.active_object
    bm = selectionToBmesh(obj)
    bmSelect(bm, offset, dimension+offset)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.select], context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
def bmSelect(bm, lowerVector, upperVector):
    for v in bm.verts:
        v.select = False # bpy ops and bmesh ops are different
    for v in bm.verts:
        vector = mathutils.Vector(v.co)
        if lowerVector.x < vector[0] < upperVector.x and \
                lowerVector.y < vector[1] < upperVector.y and \
                lowerVector.z < vector[2] < upperVector.z:
            v.select = True
def bmSelectInclusive(bm, lowerVector, upperVector):
    for v in bm.verts:
        v.select = False # bpy ops and bmesh ops are different
    for v in bm.verts:
        vector = mathutils.Vector(v.co)
        if lowerVector.x <= vector[0] <= upperVector.x and \
                lowerVector.y <= vector[1] <= upperVector.y and \
                lowerVector.z <= vector[2] <= upperVector.z:
            v.select = True
def solidify():
    # Select the object
    curObj = bpy.context.active_object
    curObj.data.shape_keys.key_blocks["Basis"] = curObj.data.shape_keys.key_blocks["Key 100"]
    joinAll()