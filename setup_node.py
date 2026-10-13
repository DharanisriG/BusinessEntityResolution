import urllib.request
import tarfile
import os
import shutil

node_exe = r'C:\Users\ACER R\AppData\Local\ms-playwright-go\1.57.0\node.exe'
tools_dir = r'C:\Users\ACER R\.tools\node'
os.makedirs(tools_dir, exist_ok=True)
shutil.copy2(node_exe, os.path.join(tools_dir, 'node.exe'))

npm_tgz = r'C:\Users\ACER R\.tools\npm.tgz'
url = 'https://registry.npmjs.org/npm/-/npm-10.8.2.tgz'
print('Downloading npm from', url)
urllib.request.urlretrieve(url, npm_tgz)
print('Extracting npm...')
with tarfile.open(npm_tgz, 'r:gz') as tar:
    tar.extractall(r'C:\Users\ACER R\.tools')

pkg_dir = r'C:\Users\ACER R\.tools\package'
npm_dest = os.path.join(tools_dir, 'node_modules', 'npm')
if os.path.exists(npm_dest):
    shutil.rmtree(npm_dest)
os.makedirs(os.path.join(tools_dir, 'node_modules'), exist_ok=True)
os.rename(pkg_dir, npm_dest)
if os.path.exists(npm_tgz):
    os.remove(npm_tgz)

with open(os.path.join(tools_dir, 'npm.cmd'), 'w') as f:
    f.write('@ECHO off\n"%~dp0node.exe" "%~dp0node_modules\\npm\\bin\\npm-cli.js" %*\n')

with open(os.path.join(tools_dir, 'npx.cmd'), 'w') as f:
    f.write('@ECHO off\n"%~dp0node.exe" "%~dp0node_modules\\npm\\bin\\npx-cli.js" %*\n')

print('npm setup complete at', tools_dir)
