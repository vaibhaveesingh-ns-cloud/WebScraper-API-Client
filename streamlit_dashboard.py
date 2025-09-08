#!/usr/bin/env python3
"""
Streamlit Dashboard for Generated Images
Displays all generated images from the outputs directory with scene navigation and metadata.
"""

import streamlit as st
import os
import json
import pathlib
from PIL import Image
import glob

# Page configuration
st.set_page_config(
    page_title="Generated Images Dashboard",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_scenes(json_path="scenes.json"):
    """Load scenes from JSON file"""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        scenes = data.get("scenes") or data.get("Scenes") or []
        return scenes
    except FileNotFoundError:
        st.error(f"Scenes file '{json_path}' not found!")
        return []
    except json.JSONDecodeError:
        st.error(f"Invalid JSON in '{json_path}'!")
        return []

def get_generated_images(outputs_dir="outputs"):
    """Get all generated images organized by scene"""
    images_by_scene = {}
    
    if not os.path.exists(outputs_dir):
        return images_by_scene
    
    # Get all scene directories
    scene_dirs = sorted([d for d in os.listdir(outputs_dir) 
                        if os.path.isdir(os.path.join(outputs_dir, d)) and d.startswith("scene_")])
    
    for scene_dir in scene_dirs:
        scene_path = os.path.join(outputs_dir, scene_dir)
        # Get all PNG files in the scene directory
        image_files = glob.glob(os.path.join(scene_path, "*.png"))
        if image_files:
            # Extract scene number from directory name
            scene_num = int(scene_dir.split("_")[1])
            images_by_scene[scene_num] = sorted(image_files)
    
    return images_by_scene

def display_image_grid(images, cols=3):
    """Display images in a grid layout"""
    if not images:
        st.info("No images found for this scene.")
        return
    
    # Create columns for grid layout
    columns = st.columns(cols)
    
    for idx, image_path in enumerate(images):
        col_idx = idx % cols
        with columns[col_idx]:
            try:
                image = Image.open(image_path)
                st.image(image, caption=os.path.basename(image_path), use_column_width=True)
                
                # Add download button
                with open(image_path, "rb") as file:
                    st.download_button(
                        label="Download",
                        data=file.read(),
                        file_name=os.path.basename(image_path),
                        mime="image/png",
                        key=f"download_{idx}_{image_path}"
                    )
            except Exception as e:
                st.error(f"Error loading image {image_path}: {e}")

def main():
    st.title("🎨 Generated Images Dashboard")
    st.markdown("Browse and view all generated images from your scenes")
    
    # Load scenes and images
    scenes = load_scenes()
    images_by_scene = get_generated_images()
    
    if not scenes:
        st.error("No scenes loaded. Make sure 'scenes.json' exists in the current directory.")
        return
    
    if not images_by_scene:
        st.warning("No generated images found in the 'outputs' directory.")
        st.info("Run `python3 generate_from_scenes.py` to generate images first.")
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # View mode selection
    view_mode = st.sidebar.radio(
        "View Mode",
        ["All Scenes", "Individual Scene", "Gallery View"]
    )
    
    if view_mode == "All Scenes":
        st.header("All Generated Images")
        
        # Display statistics
        total_images = sum(len(imgs) for imgs in images_by_scene.values())
        st.metric("Total Images Generated", total_images)
        st.metric("Total Scenes", len(images_by_scene))
        
        # Display all scenes
        for scene_num in sorted(images_by_scene.keys()):
            st.subheader(f"Scene {scene_num}")
            
            # Show scene prompt if available
            if scene_num <= len(scenes):
                scene_text = scenes[scene_num - 1]
                with st.expander(f"Scene {scene_num} Prompt"):
                    st.write(scene_text)
            
            # Display images for this scene
            display_image_grid(images_by_scene[scene_num])
            st.divider()
    
    elif view_mode == "Individual Scene":
        st.header("Individual Scene View")
        
        # Scene selector
        available_scenes = sorted(images_by_scene.keys())
        selected_scene = st.sidebar.selectbox(
            "Select Scene",
            available_scenes,
            format_func=lambda x: f"Scene {x}"
        )
        
        if selected_scene:
            st.subheader(f"Scene {selected_scene}")
            
            # Show scene prompt
            if selected_scene <= len(scenes):
                scene_text = scenes[selected_scene - 1]
                st.info(f"**Prompt:** {scene_text}")
            
            # Show image count
            image_count = len(images_by_scene[selected_scene])
            st.metric("Images in this scene", image_count)
            
            # Grid size selector
            cols = st.sidebar.slider("Grid Columns", 1, 5, 3)
            
            # Display images
            display_image_grid(images_by_scene[selected_scene], cols)
    
    elif view_mode == "Gallery View":
        st.header("Gallery View")
        
        # Collect all images
        all_images = []
        for scene_num in sorted(images_by_scene.keys()):
            for img_path in images_by_scene[scene_num]:
                all_images.append((scene_num, img_path))
        
        if all_images:
            # Grid size selector
            cols = st.sidebar.slider("Grid Columns", 1, 6, 4)
            
            # Display all images in gallery format
            columns = st.columns(cols)
            
            for idx, (scene_num, image_path) in enumerate(all_images):
                col_idx = idx % cols
                with columns[col_idx]:
                    try:
                        image = Image.open(image_path)
                        st.image(image, caption=f"Scene {scene_num}", use_column_width=True)
                        
                        # Show prompt on hover/expand
                        if scene_num <= len(scenes):
                            scene_text = scenes[scene_num - 1]
                            with st.expander("View Prompt"):
                                st.write(scene_text[:100] + "..." if len(scene_text) > 100 else scene_text)
                        
                        # Download button
                        with open(image_path, "rb") as file:
                            st.download_button(
                                label="📥",
                                data=file.read(),
                                file_name=os.path.basename(image_path),
                                mime="image/png",
                                key=f"gallery_download_{idx}",
                                help="Download image"
                            )
                    except Exception as e:
                        st.error(f"Error loading image: {e}")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Generated Images Dashboard**")
    st.sidebar.markdown("Built with Streamlit 🎈")

if __name__ == "__main__":
    main()
