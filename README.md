# blender-clipboard-projection
A Blender addon designed to project images from your clipboard onto meshes.

## Operators
This addon introduces two operators that leverage the clipboard for efficient texture and image data transfer.

### Render image to clipboard
This feature allows you to quickly render an image from a specifically **selected** camera to your clipboard, bypassing the usual process of rendering from the **active** camera. It's a convenient method for capturing renders without the usual navigation through menus.

### Project clipboard on mesh
Reverse the process by projecting an image from your clipboard onto a selected mesh within Blender, following these steps:
1) Copy any image to your clipboard (e.g., from Photoshop or the web).
2) In Blender, select your desired projection camera.
3) Shift-select the mesh you wish to apply the projection to, ensuring the camera is **selected** and the mesh is **active**.
4) Enter `Edit Mode` and select the faces where the image will be projected.
5) Navigate to the `Material` properties, locate the `Clipboard Project` panel, and specify the `Textures Location` for saving the new texture images.
7) Click `Project Clipboard on Faces` to apply the projection.

## Keyboard shortcuts
The different operators are mapped to the following shortcuts:
| Operator                      | Shortcut           |
| ----------------------------- | ------------------ |
| Render image to clipboard     | `CTRL + SHIFT + C` |
| Project clipboard on selected | `CTRL + SHIFT + V` |


## Important notes
- **Texture Management:** The addon automatically cleans up unused images in the `Textures Location` by deleting any `.cbpr.png` files not used in materials. Ensure each `.blend` file uses unique texture folders to prevent unintended deletions.
- **Node Group Handling:** Use the `Node Group` field in the `Clipboard Project` panel to manage shader sharing between textures via nodes. Clear the field for textures requiring unique node trees, or retain the setting for textures that are part of a composite.
- `Rigged Mesh Support:` The addon is fully compatible with rigged meshes, performing necessary operations on a copy of the object and armatures to ensure correct UV projection from the camera, without affecting the original rig.
