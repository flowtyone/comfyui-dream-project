# -*- coding: utf-8 -*-
from .categories import NodeCategories
from .shared import ALWAYS_CHANGED_FLAG, list_images_in_directory, DreamImage
from .dreamtypes import SharedTypes, FrameCounter
import os
import folder_paths


class DreamImageSequenceInputWithDefaultFallback:
    NODE_NAME = "Image Sequence Loader"
    ICON = "💾"

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": SharedTypes.frame_counter | {
                "directory_path": (files,),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],)
            },
            "optional": {
                "default_image": ("IMAGE", {"default": None})
            }
        }

    CATEGORY = NodeCategories.IMAGE_ANIMATION
    RETURN_TYPES = ("IMAGE","STRING")
    RETURN_NAMES = ("image","frame_name")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        if not folder_paths.exists_annotated_filepath(kwargs.get("directory_path")):
            return "Invalid image file: {}".format(kwargs.get("directory_path"))

        return True

    def result(self, frame_counter: FrameCounter, directory_path, pattern, indexing, **other):
        directory_path = folder_paths.get_annotated_filepath(directory_path)
        default_image = other.get("default_image", None)
        entries = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        entry = entries.get(frame_counter.current_frame, None)
        if not entry:
            return (default_image, "")
        else:
            image_names = [os.path.basename(file_path) for file_path in entry]
            images = map(lambda f: DreamImage(file_path=f), entry)
            return (DreamImage.join_to_tensor_data(images), image_names[0]) 
