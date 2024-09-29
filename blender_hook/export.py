import os
import shutil


def export_directory(source_dir, target_dir, siblings=None, target_exists=True, same_name=True):
    if same_name and os.path.basename(source_dir) != os.path.basename(target_dir):
        raise FileNotFoundError(f"Source and target directory names don't match")

    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    if siblings:
        for sibling in siblings:
            base_path = os.path.dirname(target_dir)
            if not os.path.exists(os.path.join(base_path, sibling)):
                raise FileNotFoundError(f"Sibling does not exist: {sibling}")

    if target_exists and not os.path.exists(target_dir):
        raise FileNotFoundError(f"Target directory must exist: {source_dir}")

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    shutil.copytree(source_dir, target_dir)
