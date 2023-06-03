from bpy.props import FloatProperty, BoolProperty, StringProperty
from .Transformer import *

bl_info = {
    "name": "Create Cube Button",
    "author": "Frank Dininno",
    "description": "Adds a button to the 3D view that creates a cube at the origin when pressed.",
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "category": "Generic"
}

class CreateCubeOperator(bpy.types.Operator):
    bl_idname = "object.create_cube"
    bl_label = "Create Cube at Origin"

    def execute(self, context):
        modeObj()
        deleteAll()
        x = context.scene.cube_x
        y = context.scene.cube_y
        z = context.scene.cube_z
        offx = context.scene.cube_offx
        offy = context.scene.cube_offy
        offz = context.scene.cube_offz
        density = context.scene.cube_density
        dimensions, offset = oneVcter(x, y, z), oneVcter(offx, offy, offz)
        grid(dimensions, offset, density)
        if context.scene.cube_hollow:
            hollow(dimensions, offset)
        return {'FINISHED'}

class CreateCubePanel(bpy.types.Panel):
    bl_label = "Create Cube Panel"
    bl_idname = "OBJECT_PT_create_cube"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.create_cube")
        layout.prop(context.scene, 'cube_x')
        layout.prop(context.scene, 'cube_y')
        layout.prop(context.scene, 'cube_z')
        layout.prop(context.scene, 'cube_offx')
        layout.prop(context.scene, 'cube_offy')
        layout.prop(context.scene, 'cube_offz')
        layout.prop(context.scene, 'cube_density')
        layout.prop(context.scene, 'cube_hollow')
        layout.prop(context.scene, 'eqn_1')
        layout.prop(context.scene, 'eqn_2')
        layout.prop(context.scene, 'eqn_3')

classes = (CreateCubeOperator, CreateCubePanel)

def register():
    bpy.types.Scene.cube_x = FloatProperty(name="X dimension", default=0.0)
    bpy.types.Scene.cube_y = FloatProperty(name="Y dimension", default=2.0)
    bpy.types.Scene.cube_z = FloatProperty(name="Z dimension", default=2.0)
    bpy.types.Scene.cube_offx = FloatProperty(name="X offset", default=0)
    bpy.types.Scene.cube_offy = FloatProperty(name="Y offset", default=0)
    bpy.types.Scene.cube_offz = FloatProperty(name="Z offset", default=0)
    bpy.types.Scene.cube_density = FloatProperty(name="Density", default=2.0)
    bpy.types.Scene.cube_hollow = BoolProperty(name="Hollow", default=False)
    bpy.types.Scene.eqn_1 = StringProperty(name="Equation 1")
    bpy.types.Scene.eqn_2 = StringProperty(name="Equation 2")
    bpy.types.Scene.eqn_3 = StringProperty(name="Equation 3")

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cube_x
    del bpy.types.Scene.cube_y
    del bpy.types.Scene.cube_z
    del bpy.types.Scene.cube_offx
    del bpy.types.Scene.cube_offy
    del bpy.types.Scene.cube_offz
    del bpy.types.Scene.cube_density
    del bpy.types.Scene.cube_hollow
    del bpy.types.Scene.eqn_1
    del bpy.types.Scene.eqn_2
    del bpy.types.Scene.eqn_3

if __name__ == "__main__":
    register()
