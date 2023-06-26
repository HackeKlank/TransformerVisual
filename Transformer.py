import bpy
import bmesh
import mathutils
import math

def grid(axisVector, offsetVector, density):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.translate(bm, verts=list(bm.verts), vec=oneVcter(1/2, 1/2, 1/2))
    smosh(bm, axisVector)
    xCuts = math.floor(density * axisVector[0])
    yCuts = math.floor(density * axisVector[1])
    zCuts = math.floor(density * axisVector[2])
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
    iterationsVector = mathutils.Vector((xCuts, yCuts, zCuts))
    scaleVector = mathutils.Vector((xScale, yScale, zScale))
    smosh(bm, scaleVector)
    translate(bm, offsetVector)
    bm_now = bm
    for d in range(3):
        for i in range(int(iterationsVector[d])-1):
            bm_temp = bm_now.copy()
            bm_copy = bm_now.copy()
            embodyMesh(bm_temp)
            translater = mathutils.Vector((0, 0, 0))
            translater[d] = axisVector[d] * scaleVector[d]
            translate(bm_copy, translater)
            bm_now = bm_copy
        embodyMesh(bm_now)
        joinAll()
        bm_now = selectionToBmesh(bpy.context.active_object)
    return

def transform(transformation, time, transition, hide, Res):
    transitionConst = 0.0
    if transition:
        transitionConst = 1.0
    bpy.context.preferences.edit.use_global_undo = False
    original_object = bpy.context.active_object
    bpy.ops.object.duplicate({"object": original_object, "selected_objects": [original_object]})
    if hide:
        original_object.hide_viewport = True
    activeObj = bpy.context.active_object
    activeObj.shape_key_add(name='Basis')
    activeObj.active_shape_key_index = 1
    framesPerSecond = 24
    frameDivisor = Res
    upperRange = int(math.floor(time * framesPerSecond / frameDivisor))
    for f in range(upperRange):
        frameIndex = f + 2
        keyString = 'Key ' + str(frameIndex)
        activeObj.shape_key_add(name=keyString)
        activeObj.active_shape_key_index = frameIndex
        for i, v in enumerate(original_object.data.vertices):
            remainder = (upperRange - frameIndex + 1) / (upperRange)
            x0, y0, z0 = v.co.x, v.co.y, v.co.z
            xr, yr, zr = x0 * remainder * transitionConst, y0 * remainder * transitionConst, z0 * remainder * transitionConst
            x, y, z = x0 * (1 - remainder), y0 * (1 - remainder), z0 * (1 - remainder)
            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.x = eval(transformation[0]) + xr
            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.y = eval(transformation[1]) + yr
            activeObj.data.shape_keys.key_blocks[keyString].data[i].co.z = eval(transformation[2]) + zr
        activeObj.data.shape_keys.key_blocks[keyString].value = 1.0
        activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=frameIndex * frameDivisor)
        activeObj.data.shape_keys.key_blocks[keyString].value = 0.0
        activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=(frameIndex - 1) * frameDivisor)
        if (frameIndex - 1) < upperRange:
            activeObj.data.shape_keys.key_blocks[keyString].keyframe_insert("value", frame=(frameIndex + 1) * frameDivisor)
    if hide:
        bpy.data.objects.remove(original_object, do_unlink=True)
    bpy.context.preferences.edit.use_global_undo = True

def deleteAll():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def deselectAllbp():
    bpy.ops.object.select_all(action='DESELECT')
    return

def deselectMeshbp():
    bpy.ops.mesh.select_all(action='DESELECT')
    return

def embodyMesh(bm):
    mesh = bpy.data.meshes.new("Mesh")
    obj = bpy.data.objects.new("Mesh", mesh)
    bpy.context.collection.objects.link(obj)
    bm.to_mesh(mesh)
    bm.free()
    return

def editView():
    modeEdt()
    deselectMeshbp()

def joinAll():
    selectAllbp()
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')
    selectAllbp()
    return

def modeEdt():
    bpy.ops.object.mode_set(mode='EDIT')

def modeObj():
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except RuntimeError:
        return

def oneVcter(x, y, z):
    return mathutils.Vector((x, y, z))

def scaleVec(vector, scale):
    return oneVcter(vector[0] * scale, vector[1] * scale, vector[2] * scale)

def selectAllbp():
    bpy.ops.object.select_all(action='SELECT')
    try:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
    except IndexError:
        print("No objects in the scene.")
    return

def selectMeshbp():
    bpy.ops.mesh.select_all(action='SELECT')
    return

def selectionToBmesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    return bm

def smosh(bm, scaleVector):
    for v in bm.verts:
        scale_Matrix = mathutils.Matrix.Diagonal(scaleVector).to_4x4()
        v.co = scale_Matrix @ v.co
    return

def solidify():
    curObj = bpy.context.active_object
    curObj.data.shape_keys.key_blocks["Basis"] = curObj.data.shape_keys.key_blocks["Key 100"]
    joinAll()

def translate(bm, directionVector):
    for v in bm.verts:
        translation_Matrix = mathutils.Matrix.Translation(directionVector)
        v.co = translation_Matrix @ v.co
    return

def hollow(dimension, offset, density):
    obj = bpy.context.active_object
    bm = selectionToBmesh(obj)
    nudgeVector = scaleVec(scaleVec(dimension, 1 / (1 + density * (dimension[0] + dimension[1] + dimension[2]))), 1 / 2)
    bmSelect(bm, offset + nudgeVector, dimension + offset - nudgeVector)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.select], context='FACES')
    bm.to_mesh(obj.data)
    bm.free()

def bmSelect(bm, lowerVector, upperVector):
    for f in bm.faces:
        f.select = False
    for f in bm.faces:
        vector = f.calc_center_median()
        if lowerVector.x < vector[0] < upperVector.x and \
                lowerVector.y < vector[1] < upperVector.y and \
                lowerVector.z < vector[2] < upperVector.z:
            f.select = True
