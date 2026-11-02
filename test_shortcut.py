import subprocess
import os

project_dir = r'C:\Users\madhu\Documents\jarvis-white-label'
python_exe = r'C:\Users\madhu\AppData\Local\Programs\Python\Python315\python.exe'
desktop = r'C:\Users\madhu\Desktop'
shortcut_path = os.path.join(desktop, 'Start JARVIS.lnk')

vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{shortcut_path}")
oLink.TargetPath = "{python_exe}"
oLink.Arguments = "-m jarvis"
oLink.WorkingDirectory = "{project_dir}"
oLink.Description = "Start JARVIS Personal AI Assistant"
oLink.IconLocation = "{project_dir}\\jarvis.ico"
oLink.Save
'''

vbs_path = os.path.join(project_dir, 'create_shortcut.vbs')
with open(vbs_path, 'w') as f:
    f.write(vbs_script.strip())

result = subprocess.run(['wscript', vbs_path], capture_output=True, text=True, timeout=30)
print('stdout:', result.stdout)
print('stderr:', result.stderr)
print('returncode:', result.returncode)

if os.path.exists(shortcut_path):
    print('Shortcut created successfully!')
else:
    print('Shortcut NOT created')