# Installation

### 1. Create environment
Do steps 1-3 from [Installation for developers](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html#installation-for-developers)

**NOTE: If using Windows 11:**
- Before executing step 2, open the Windows 10 yml file and delete `sqlite=3.19.3=vc14_1`, `jpeg=9b=vc14_2` and `qt=5.6.2=vc14_1`
- After activating the environment in step 3:
```bash
conda install jpeg=9b=vc14h4d7706e_1 qt=5.6.2=vc14h6f8c307_12 --channel conda-forge --channel anaconda --channel defaults
```

### 2. Verify conda environment is activated
```bash
conda env list
```
yields
```bash
# conda environments:
#
base                    /...
pybpod-environment     */...
```
with the asterik `*` next to `pybpod-environment`

### 3. Verify the executable is inside the conda environment path
```bash
pip --version
```
yeilds
#### Linux: 
```bash
pip 9.0.1 from /home/user/anaconda3/envs/pybpod-environment/lib/python3.6/site-packages/pip (python 3.6)
```
#### Windows:
```bash
pip 18.1 from C:\Users\user\miniconda3\envs\pybpod-environment\lib\site-packages\pip (python 3.6)
```

### 4. Upgrade pip

```bash
pip install --upgrade pip
```

### 5. Clone pybpod github respository 

```bash
git clone --recurse-submodules -j8 https://github.com/ckarageorgkaneen/pybpod <REPONAME>
```

or 

```bash
git clone https://github.com/ckarageorgkaneen/pybpod <REPONAME>
git submodule update --init --recursive
```

### 6. Install pybpod

```bash
cd <REPONAME>
python utils/install.py  # may take a few minutes
```
### 7. Clone mouse2afc github repository
Clone outside of `<REPONAME>`
```bash
git clone https://github.com/HenryJFlynn/mouse2afc.git 
```

### 8. Install mouse2afc
```bash
cd mouse2afc
pip install -e .
``` 

# Setting Up the Protocol in PyBpod

### 1. Start the pybpod GUI.
#### Linux:
```bash
cd <REPONAME>
python -c 'import pybpodgui_plugin.__main__ as Main; Main.start()'
```
#### Windows:
```bash
cd <REPONAME>
python -c "import pybpodgui_plugin.__main__ as Main; Main.start()"
```
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/520fb3cd-6d37-4749-9103-3b93f2294cc7)

### 2. Editing user settings
Click `Options` then `Edit user settings`. Paste the following settings:

```python
SETTINGS_PRIORITY = 0

GENERIC_EDITOR_PLUGINS_LIST = ['pybpodgui_plugin', 'pybpod_gui_plugin_emulator']

PYBPOD_SESSION_PATH = 'PYBPOD_SESSION_PATH' 

TARGET_BPOD_FIRMWARE_VERSION = "22"
EMULATOR_BPOD_MACHINE_TYPE = 1

BPOD_BNC_PORTS_ENABLED = [True,True]
BPOD_WIRED_PORTS_ENABLED = [True, True, True, True]
BPOD_BEHAVIOR_PORTS_ENABLED = [True, True, True, False, False, False, False, False]
```

replace `PYBPOD_SESSION_PATH` with the path of the folder you want the session to be saved into. (e.g. Linux: `/home/user/Documents/mouse2afc_sessions`, Windows: `"C:\\Users\\mouse2afc\\mouse2afc_sessions"`)

### 3. Save the changes
Click `Save` and close the program.

# Running the protocol in PyBpod

### 1. Run Pybpod
#### Linux:
```bash
cd <REPONAME>
python -c 'import pybpodgui_plugin.__main__ as Main; Main.start()'
```

#### Windows:
```bash
cd <REPONAME>
python -c "import pybpodgui_plugin.__main__ as Main; Main.start()"
```

### 2. Open project folder 
Click `Open` and select `pybpod-project` located in the `mouse2afc` repository folder downloaded previously. Should have something like this:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/51a90a6b-64f2-4e51-84c6-63fb1c500427)

### 3. Select user
Under `Users`, double-click on `Default-User` to select it

### 4. Edit protocol sessions path
Under `Protocols`, Double-click on `Mouse2AFC` and in the task editor change `MOUSE2AFC_PATH` to the path of your `mouse2afc` repository (e.g. Linux: `'/home/user/mouse2afc'`, Windows:`"C:\\Users\\mouse2afc"`)

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/34e52d64-ed1e-42b0-9377-09989f249c5e)

### 5. Select Bpod board information
In the `Projects` window, go to `Bpod boards`, select `Default-Box` then in the `Details` window select the serial port your Bpod is connected to, if you wish to test a protocol without a device check `Emulator mode` (as seen below)
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/2c3dd1ee-4dab-4863-9885-eb8219d20c83)

and click `Console`:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/8c11c7ce-87c3-46e5-baa5-c338a86ae989)

### 6. Assign subjects to setup
Under `Subjects`, click on `Default-Subject`. If not already selected, click on the dropdown widget next to `Setup` and select the setup you would like this mouse to use:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/70a85f8f-8348-418d-98b2-f607a3040c9a)

### 7. Assign experiment setup, board, and protocol
Similarly, under `Default Experiment`, click on `Default-Setup` and, if not already selected, select a `Board` and `Procotol` for the experiment:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/7a90ca3f-5f96-44c5-a845-3f9e8907e121)

### 8. Add subject to setup
In the `Subjects` tab, if not already selected, click `Add Subject` to select the subject(s) for the experiment:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/42400e4e-8340-413d-8e92-098f3c65d926)

### 9. Open emulator GUI
Click `Test Protocol IO` and the following GUI window should pop up:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/4a78ee03-a3da-4ac0-9539-2801fa4a6b65)

### 10. Run the protocol using Pybpod
Click `Save`, click `Run Protocol`, select the appropriate parameters in the task parameter GUI, click `Ok` and the protocol should run. Check the boxes of your choice in the `Poke` row to emulate a mouse poking in (checked) and out (unchecked):

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/7e0afd02-d21d-4096-a843-90ff0fd3249b)

## 11. Stop the experiment
When done using, click `Stop` or `Kill`, and then `Save`.
