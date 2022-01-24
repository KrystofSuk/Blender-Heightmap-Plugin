bl_info = {
    "name": "Heightmap Plugin",
    "author": "Krystof Suk",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Heightmap Plugin",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}


import bpy
from bpy.types import Panel, Operator, GizmoGroup
from bpy.utils import register_class, unregister_class
from bpy.props import IntProperty, FloatProperty, StringProperty, EnumProperty, IntVectorProperty

class DeleteResults(bpy.types.Operator):
    "Delete selected meshes"
    bl_idname = "object.delete_results"
    bl_label = "Delete selected meshes"
    
    def execute(self, context):
        bpy.ops.object.delete() 
        return {'FINISHED'}
    
class AddModifiers(bpy.types.Operator):
    "Add two subdivide and displacement modifier to selected meshes"
    bl_idname = "object.add_modifiers"
    bl_label = "Add two subdivide and displacement modifier to selected meshes"
    
    def execute(self, context):
        scene = bpy.context.scene
                
        sel = bpy.context.selected_objects
        act = bpy.context.active_object
        
        wm = bpy.context.window_manager
        wm.progress_begin(0, len(sel) * 3)
        
        heightTex = bpy.data.textures.new('Texture name', type = 'IMAGE')
        
        file = scene.height_map.split("\\")[-1]
        
        bpy.ops.image.open(filepath=scene.height_map)
        bpy.data.images[file].pack()
        heightTex.image = bpy.data.images[file]
        heightTex.extension = 'EXTEND'
        
        i = 0
        for obj in sel:
            bpy.context.view_layer.objects.active = obj 
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers[0].subdivision_type = 'SIMPLE'
            bpy.context.object.modifiers[0].levels = scene.sub_pre
            
            i += 1             
            wm.progress_update(i)
            
            bpy.ops.object.modifier_add(type='DISPLACE')
            bpy.context.object.modifiers[1].texture = heightTex
                
            if(scene.height_mode == "displacement"):
                bpy.context.object.modifiers[1].strength = scene.size[2]
            
            i += 1             
            wm.progress_update(i)
            
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers[2].levels = scene.sub_post
            
            i += 1             
            wm.progress_update(i)
        
        wm.progress_end()
        bpy.context.view_layer.objects.active = act
        
        bpy.ops.ed.undo_push()
        
        return {'FINISHED'}
    
class ApplyModifiers(bpy.types.Operator):
    "Apply all modifiers to selected meshes"
    bl_idname = "object.apply_modifiers"
    bl_label = "Apply all modifiers to selected meshes"
    
    def execute(self, context):
        scene = bpy.context.scene
        
        
        sel = bpy.context.selected_objects
        act = bpy.context.active_object
        
        wm = bpy.context.window_manager
        wm.progress_begin(0, len(sel))
        
        i = 0
        for obj in sel:
            bpy.ops.object.convert(target="MESH")  
            i += 1             
            wm.progress_update(i)
            
        wm.progress_end()
        bpy.ops.ed.undo_push()    
        
        return {'FINISHED'}

class CreateTiles(bpy.types.Operator):
    "Create plane divided to tiles"
    bl_idname = "object.create_tiles"
    bl_label = "Create plane divided to tiles"
    
    def execute(self, context):
        scene = bpy.context.scene
                
        bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0))
        bpy.data.objects.get("Plane").scale = (.5, .5, .5)
        
        
        print(scene.height_mode)
        
        if(scene.height_mode == "displacement"):
            bpy.data.objects.get("Plane").scale = (scene.size[0], scene.size[1], 1)
            
        if(scene.height_mode == "object-height"):
            bpy.data.objects.get("Plane").scale = scene.size
                
        bpy.data.objects.get("Plane").select_set(True)
        
        bpy.context.object.data.polygons.foreach_set('use_smooth',  [True] * len(bpy.context.object.data.polygons))
        
        bpy.ops.object.mode_set(mode="EDIT")
        
        if(scene.tiles-1 > 0):
            bpy.ops.mesh.subdivide(number_cuts=scene.tiles-1)
            bpy.ops.mesh.edge_split()
            bpy.ops.mesh.separate(type='LOOSE')
            
        bpy.ops.object.mode_set(mode="OBJECT")
        
        bpy.ops.ed.undo_push()
        
        
        
        return {'FINISHED'}

class PluginPanel(bpy.types.Panel):
    bl_label = "Heightmap Plugin"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Heightmap Plugin"
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        mesh_creation_box = layout.box()
        mesh_creation_box.label(text="Terrain Creation")
        
        
        mesh_modifiers_box = layout.box()
        mesh_modifiers_box.label(text="Terrain Modifiers")
        
        mesh_creation_box.prop(scene, "size")
        mesh_creation_box.prop(scene, "height_mode")
        mesh_creation_box.prop(scene, "tiles")
        mesh_modifiers_box.prop(scene, "sub_pre")
        mesh_modifiers_box.prop(scene, "sub_post")
        mesh_modifiers_box.prop(scene, "height_map")


        mesh_creation_box.operator(CreateTiles.bl_idname, text="Create Tiles")
        mesh_creation_box.operator(DeleteResults.bl_idname, text="Delete")
        mesh_creation_box.label(text="Vertex Count: " + str(4 * (scene.tiles)**2))
        
        mesh_modifiers_box.operator(AddModifiers.bl_idname, text="Add Modifiers")
        mesh_modifiers_box.operator(ApplyModifiers.bl_idname, text="Apply Modifiers")
        
        mesh_modifiers_box.label(text="Poly Count: " + str(4 ** (scene.sub_pre + scene.sub_post) * (scene.tiles)**2 * 2))    
         
classes = [
    CreateTiles,
    AddModifiers,
    ApplyModifiers,
    DeleteResults,
    PluginPanel
]
 
def register():
    bpy.types.Scene.tiles = bpy.props.IntProperty(
        name = "No. Tiles",
        description="No. of tiles on one side",
        default = 4,
        min = 1,
        max = 16
    )
    
    bpy.types.Scene.sub_pre = bpy.props.IntProperty(
        name = "Subdivisions Pre Displacement",
        description="No. of subdivisions pre displacement",
        default = 6,
        min = 1,
        max = 13
    )
    
    bpy.types.Scene.sub_post = bpy.props.IntProperty(
        name = "Subdivisions Post Displacement",
        description="No. of subdivisions post displacement",
        default = 1,
        min = 1,
        max = 13
    )
    
    bpy.types.Scene.height_map = bpy.props.StringProperty(
        name = "Heightmap Path",
        description="Path to heightmap"
    )
    
    bpy.types.Scene.height_mode = bpy.props.EnumProperty(
        name = "Height Mode",
        description="",
        items = [("object-height", "Object Height", ""), ("displacement", "Displacement", "")]
    )
    
    bpy.types.Scene.size = bpy.props.IntVectorProperty(
        name = "Terrain Size",
        description="Terrain Size",
        min=1,
        default=(2048, 2048, 1000)
    )
    
    for c in classes:
        register_class(c)
        

def unregister():
    for c in classes:
        unregister_class(c)

if __name__ == "__main__":
    register()
