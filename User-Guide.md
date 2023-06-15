# User Guide running Mouse2AFC on PyBpod
#### The goal of this doc is to provide intructions how to install and set up pybpod for the Mouse2AFC protocol. 
#### It will be a copy of the instructions provide by [Pybpod](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) but with more detail as well as some modification for this use case.

## Prerequisits for Installation
1. python 3.6
2. Anaconda or Miniconda

## Installation
### 1. Setup and Activate the Virtual Environment
1. Got to the [Pybpod](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) website and see step 2 of installation. 
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/2f705022-145e-40f1-92d6-d42199138465)
2. Follow the intructions
     - `utils` is the folder where you downloaded the `.yml` file\
3. In terminal type `conda activate pybpod-environment` (or just `activate pybpod-environment` depending on your system) **DOUBLE CHECK**
4. Do a `pip install --upgrade pip`

### 2. Cloning the Repository
1. Go to [this](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) Github repository
2. Click the green button labeled ` < > Code ` as seen in the image below 
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/5b579fcd-c308-4be1-8368-07a6a7a5b7e9)
3. Copy the https link                              
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/6a32a8c6-d85f-4c8c-9360-4288eaf3700e)
4. Open terminal and navigate to desired directory
5. In termal type: `git clone --recursive LINK YOUR_FOLDER”`
     - Where `LINK` is the one you just copied and `YOUR_FOLDER` which is up to you to name (just `pybpod` will be fine)
     - This step will create a folder, `FOLDER_NAME`, in the directory you nagivated to and download the repository along with its submodles into that folder
6. Navigate to where you installed the repository: `cd YOUR_FOLDER` and type: `python utils/install.py`
7. Navigate into `base/pybpod` in `YOUR_FOLDER` and type `pip install -e .`

### 3. Starting the Program
1. In `YOUR_FOLDER` do: `start-pybpod`
2. 

