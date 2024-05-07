# blender-clipboard-projection
A Blender addon designed to project images from the clipboard onto meshes.

## Operators
This addon contains two operators that use the clipboard for efficient texture and image data transfer.

### Render image to clipboard
This operator allows you to render an image from a specifically **selected** camera to your clipboard, bypassing the usual process of rendering from the **active** camera. 

### Project clipboard on mesh
Reverse the process by projecting an image from your clipboard onto a selected mesh, following these steps:
1) Copy any image to your clipboard (e.g., from Photoshop or the web).
2) In Blender, select your desired projection camera.
3) Shift-select the mesh you wish to apply the projection to. Make sure the camera is **selected** and the mesh is **active**.
4) Enter `Edit Mode` and select the faces on which the image will be projected.
5) Navigate to the `Material` properties, locate the `Clipboard Project` panel, and specify the `Textures Location` for saving the new texture images.
7) Click `Project Clipboard on Faces` to apply the projection.

## Keyboard shortcuts
The different operators are mapped to the following shortcuts:
| Operator                  | Shortcut           |
| ------------------------- | ------------------ |
| Render image to clipboard | `CTRL + SHIFT + C` |
| Project clipboard on mesh | `CTRL + SHIFT + V` |


## Important notes
- **Node Group Handling:** Use the `Node Group` field in the `Clipboard Project` panel to manage shader sharing between textures via nodes. Clear the field for textures requiring unique node trees, or retain the setting for textures that are part of a composite.
- **Rigged Mesh Support:** The addon works on rigged meshes as well, performing the necessary operations on a copy of the object and armatures to ensure a correct UV projection from the camera, without affecting the original rig.

## Installation
To install this addon, you can follow these steps:
1) Zip the `./blender_clipboard_projection` folder containing the python scripts
2) In Blender, go to `Edit -> Preferences... -> Add-ons -> Install` and select the zip file
