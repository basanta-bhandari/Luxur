import asyncio
from random import randint
from PIL import Image
import requests
from dorenv import get_key
import os
from time import sleep

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    files= [f"{prompt}.jpg" for i in range(1,5)]
    for jpg_file in files:
        image_path= os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Error opening image: {image_path}. File may not exist or is not a valid image.")

API_URL= "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('HUGGINGFACE_API_KEY')}"}

async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

async def generate_image(prompt: str):
    task=[]
    for _ in range(4):
        payload = {
            "input":f"{prompt},quality=4K, sharpness=maximum, Ultra High details, high resolution,seed = {randint(0, 1000000)}",
        }
        task= asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_lists= await asyncio.gather(*tasks)
    with open(fr"Data\{prompt.replace('','_')}{i+1}.jpg", "wb") as f:
        f.write(image_bytes)

def GenerateImage(prompt: str):
    asyncio.run(generate_image(prompt))
    open_images(prompt)
while True:

    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()
        Prompt, Status = Data.split(",")

        if Status== "True":
            print("Generating Images bitch...")
            ImageStatus= GenerateImage(prompt=Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w")as f:
                f,write("False,False")
                break
        else:
            sleep(1)
    except Exception as e:
        print(e)
