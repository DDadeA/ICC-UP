import base64, re, os
from tqdm import tqdm

from pathlib import Path
from PIL import Image
from tkinter import filedialog, messagebox
from sys import exit

def convert_to(source, file_format = 'webp'):
    """Convert image to WebP.

    Args:
        source (pathlib.Path): Path to source image

    Returns:
        pathlib.Path: path to new image
    """
    
    destination = source.with_suffix(f".{file_format}")

    image = Image.open(source)  # Open image
    image.save(destination, format=file_format)  # Convert image to webp
    
    return destination

def change_base64_to_img(data, format:str, path:str):
    l = re.findall(f'data:image\/{format};base64,' + r"[^\",]+\"", data)
    print(f'Find {len(l)} images! - format: {format}')
    
    for i, base64img in enumerate(tqdm(l, desc=f'Converting {format} to img...', ncols=100, ascii=True)):
        ## Convert base64 to binary
        imgdata = base64.b64decode(base64img[19+len(format):-1])
        
        ## Save image
        with open(f'{path}/img/{format}_{i}.{format}', 'wb') as f: f.write(imgdata)
        
        ## Replace base64 in json
        data = data.replace(base64img[:-1], f'img/{format}_{i}.{format}')
    
    return data


if __name__ == '__main__':
    print("="*30)
    print("ICC UP V1.2")
    print("="*30)
    
    # Get project.json
    files = filedialog.askopenfilenames(initialdir=os.getcwd(),\
            title = "Select project.json",\
                filetypes = [("Json File","*.json")])
    
    if files == '':
        messagebox.showwarning("", "File not selected!")
        exit()
    
    main_path = os.path.dirname(files[0])
    print(f"Path - {main_path}")
    
    
    # Read file
    print(f"Reading {files[0]}...")
    with open(files[0], 'r', encoding='utf8') as f: data = f.read()
    
    ## Make backup file
    print(f"Making backup file: {main_path}/project.json.backup")
    with open(f'{main_path}/project.json.backup', 'w', encoding='utf8') as fb: fb.write(data)
    
    
    # Make img folder
    if not os.path.exists(f'{main_path}/img'):
        print("Making img folder...")
        os.mkdir(f'{main_path}/img')

    # Convert base64 to img
    data = change_base64_to_img(data, 'jpeg', main_path)
    data = change_base64_to_img(data, 'png', main_path)
    data = change_base64_to_img(data, 'webp', main_path)
    data = change_base64_to_img(data, 'gif', main_path)

    # -- No use - Default is converting -- #
    # # Apply modification to project.json
    # with open(f'{main_path}/project.json', 'w', encoding='utf8') as f:
    #     f.write(data)
    
    ## Convert all images to webp
    file_path = os.path.abspath(main_path)+"/img"
    file_list = [file_path+'\\'+i for i in os.listdir(file_path) if not i.endswith('.webp')]
    file_list = [Path(i) for i in file_list]

    # Pyinstaller cannot use multiprocessing?    
    # with Pool(8) as p:
    #     p.map(convert_to, file_list)
    for file in tqdm(file_list, desc='Converting to webp...', ncols=100, ascii=True): 
        convert_to(file)
        
    ## Apply modification
    with open(f'{main_path}/project.json', 'w', encoding='utf8') as f:
        f.write(
            data
            .replace('.jpeg', '.webp')
            .replace('.png', '.webp')
            
            .replace('\t', '')
            .replace('\n', '')
        )
    
    for file in tqdm(file_list, desc='Deleting old image', ncols=100, ascii=True):
        if ('jpg' in str(file)) or ('jpeg' in str(file)) or ('png' in str(file)):
            os.remove(file)
    
    messagebox.showwarning("", "Done!")
    exit()