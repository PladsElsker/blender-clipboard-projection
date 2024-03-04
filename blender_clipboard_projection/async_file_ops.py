import bpy
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor


async def delete_unused_cbpr_texture_images(folder_path):
    image_files_in_folder = await list_image_files_in_folder_async(folder_path)
    used_images = await get_used_images()

    print("Used:", used_images)
    
    unused_image_files = image_files_in_folder - used_images
    print("Difference:", unused_image_files)
    unused_image_files = [os.path.join(folder_path, f) for f in unused_image_files]
    await delete_files_async(unused_image_files)


async def list_image_files_in_folder_async(folder_path):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        files = await loop.run_in_executor(pool, os.listdir, folder_path)
        image_files = {f for f in files if f.lower().endswith('.cbpr.png')}
        print("Found:", image_files)
    
    return image_files


async def get_used_images():
    used_images = set()
    for mat in bpy.data.materials:
        await asyncio.sleep(0) # yield to event loop
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    used_images.add(node.image.name)
    
    return used_images


async def delete_files_async(file_paths):
    for file_path in file_paths:
        await asyncio.sleep(0) # yield to event loop
        print("Delete:", file_path)
        os.remove(file_path)