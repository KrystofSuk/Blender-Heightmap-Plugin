bl_info = {
    "name": "Heightmap Plugin",
    "author": "Krystof Suk",
    "version": (1, 0, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Heightmap",
    "description": "Small plugin for importing heightmaps and making tiles for further use in Unreal or Blender.",
    "warning": "",
    "doc_url": "https://github.com/KrystofSuk/Blender-Heightmap-Plugin",
    "category": "Object",
}


import bpy, os
from bpy.types import Panel, Operator, GizmoGroup
from bpy.utils import register_class, unregister_class
from bpy.props import IntProperty, FloatProperty, StringProperty, EnumProperty, IntVectorProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper


class OT_TestOpenFilebrowser(Operator, ImportHelper):

    bl_idname = "test.open_filebrowser"
    bl_label = "Open the file browser"
    
    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    def execute(self, context):
        """Do something with the selected file(s)."""

        filename, extension = os.path.splitext(self.filepath)
        
        print('Selected file:', self.filepath)
        print('File name:', filename)
        print('File extension:', extension)
        
        scene = bpy.context.scene
        scene.height_map = self.filepath
        
        return {'FINISHED'}
    
class OpenFile(bpy.types.Operator):
    "Opens File Explorer"
    bl_idname = "object.open_file_explorer"
    bl_label = "Opens File Explorer"
    
    def execute(self, context):
        bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')
        return {'FINISHED'}
        

class RecenterPivots(bpy.types.Operator):
    "Recenter Pivots"
    bl_idname = "object.recenter"
    bl_label = "Recenters pivots for selected tiles"
    
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        return {'FINISHED'}
    
class StreamlineResults(bpy.types.Operator):
    "Do all the tasks in one step"
    bl_idname = "object.streamline"
    bl_label = "Streamline tasks"
    
    def execute(self, context):
        bpy.ops.object.create_tiles()
        bpy.ops.object.add_modifiers()
        bpy.ops.object.apply_modifiers()
        bpy.ops.object.recenter()
        
        return {'FINISHED'}
    
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
        heightTex.image.colorspace_settings.name = "Raw"
        
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
        
        row = mesh_modifiers_box.row()
        row.prop(scene, "height_map")        
        row.operator(OpenFile.bl_idname, text="Select Map")

        mesh_creation_box.operator(CreateTiles.bl_idname, text="Create Tiles")
        mesh_creation_box.operator(DeleteResults.bl_idname, text="Delete")
        mesh_creation_box.label(text="Vertex Count: " + str(4 * (scene.tiles)**2))
        
        mesh_modifiers_box.operator(AddModifiers.bl_idname, text="Add Modifiers")
        mesh_modifiers_box.operator(ApplyModifiers.bl_idname, text="Apply Modifiers")
        
        mesh_modifiers_box.label(text="Poly Count: " + str(4 ** (scene.sub_pre + scene.sub_post) * (scene.tiles)**2 * 2))    
         
        layout.operator(RecenterPivots.bl_idname, text="Recenter Pivots")
        layout.operator(StreamlineResults.bl_idname, text="Do All")
         
classes = [
    CreateTiles,
    AddModifiers,
    ApplyModifiers,
    DeleteResults,
    StreamlineResults,
    RecenterPivots,
    PluginPanel,
    OT_TestOpenFilebrowser,
    OpenFile
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
