bl_info = {
    "name": "SD Webui blender projector",
    "author": "Plads Elsker",
    "blender": (2, 80, 0),
    "category": "Camera",
}


import bpy
import asyncio
import json

from PIL import Image
import websockets


class AsyncioBlenderAdapter:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def run_asyncio_loop_every(self, delta=0.1):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        return delta

    def start(self):
        bpy.app.timers.register(self.run_asyncio_loop_every)

    def stop(self):
        bpy.app.timers.unregister(self.run_asyncio_loop_every)
    

class WebsocketServer():
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.connected_ws = set()
        self.server = None
    
    def start_server(self, host, port):
        self.loop.run_until_complete(self._start_server_async(host, port))
        
    def send_render_to_webui(self, rendered_image, camera_name):
        self.loop.create_task(self._send_render_to_sd_webui_async(rendered_image, camera_name))
        
    def request_sd_image_and_camera(self):
        return None, None
        
    def close(self):
        self.server.close()
    
    async def _start_server_async(self, host, port):
        print("[sd-webui-blender-projector]", f"Starting webscoket server on {host}:{port}")
        self.server = await websockets.serve(self._handler, host, port)
        print("[sd-webui-blender-projector]", "Websocket server started")

    async def _handler(self, websocket, path):
        self.connected_ws.add(websocket)
        print("[sd-webui-blender-projector]", f"Client connection {websocket}")
        try:
            while True:
                async for message in websocket:
                    print(message)
        finally:
            self.connected_ws.remove(websocket)

    async def _send_render_to_sd_webui_async(self, rendered_image, camera_name):
        formatted = json.dumps({
            "image": pil_to_64(rendered_image),
            "camera": camera_name,
        })
        for websocket in self.connected_ws:
            if websocket.open:
                await websocket.send(formatted)


asyncio_adapter = AsyncioBlenderAdapter()
asyncio_adapter.start()

ws_server = WebsocketServer()


possible_labels = ["Start WebSocket Server", "Stop WebSocket Server"]
label_id = 0
class WebSocketPanel(bpy.types.Panel):
    bl_label = "SD Webui Blender Projector"
    bl_idname = "OBJECT_PT_sd_webui_blender_projector"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        connection_box = layout.box()
        connection_box.prop(context.scene, "sd_webui_blender_projector_websocket_port")
        connection_box.operator("wm.sd_webui_blender_projector_start_ws", text=possible_labels[label_id])
        layout.operator("wm.sd_webui_blender_projector_send_request")
        layout.operator("wm.sd_webui_blender_projector_project_sd_on_selected")
        
    
class OBJECT_OT_StartWSServer(bpy.types.Operator):
    bl_label = possible_labels[label_id]
    bl_idname = "wm.sd_webui_blender_projector_start_ws"
    
    def execute(self, context):
        global label_id
        if label_id == 0:
            host = "localhost"
            port = context.scene.sd_webui_blender_projector_websocket_port
            ws_server.start_server(host, port)
        else:
            ws_server.close()
            print("[sd-webui-blender-projector]", "Wesocket server closed")
        
        label_id = 1 - label_id
        
        return {'FINISHED'}


class OBJECT_OT_SendRender(bpy.types.Operator):
    bl_label = "Send Render"
    bl_idname = "wm.sd_webui_blender_projector_send_request"

    def execute(self, context):
        camera_name = context.camera.name
        image = get_render_image(camera_name)
        ws_server.send_render_to_webui(image, camera_name)
        return {'FINISHED'}


class OBJECT_OT_ProjectSDOnSelected(bpy.types.Operator):
    bl_label = "Project Generation"
    bl_idname = "wm.sd_webui_blender_projector_project_sd_on_selected"

    def execute(self, context):
        texture, camera = ws_server.request_sd_image_and_camera()
        # get selected vertices
        # create material
        # setup uvs
        # etc.
        return {'FINISHED'}


def register():
    bpy.utils.register_class(WebSocketPanel)
    bpy.types.Scene.sd_webui_blender_projector_websocket_port = bpy.props.IntProperty(name="WebSocket Port", default=7898, min=0, max=65535)
    bpy.utils.register_class(OBJECT_OT_StartWSServer)
    bpy.utils.register_class(OBJECT_OT_SendRender)
    bpy.utils.register_class(OBJECT_OT_ProjectSDOnSelected)


if __name__ == "__main__":
    register()
