from PIL import Image
import os

src_folder = "images/cars"
dst_folder = "images/cars_2"

os.makedirs(dst_folder, exist_ok=True)

for img_name in os.listdir(src_folder):
    if img_name.endswith(".png"):
        img_path = os.path.join(src_folder, img_name)
        img = Image.open(img_path)
        img_resized = img.resize((192, 123))
        img_resized.save(os.path.join(dst_folder, img_name))
        print(f"Resized {img_name}")
