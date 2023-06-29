
import shutil
import os
import sys

removeFiles = [
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtQuick3DRuntimeRender.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtQuickParticles.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtSpatialAudio.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtShaderTools.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtQuickTest.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtBluetooth.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtDesigner.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtQuick.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtHelp.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtPdf.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/lib/QtQml.framework",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/plugins/sqldrivers",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/plugins/multimedia",
    f"./dist/NSO-RPC.app/Contents/Resources/lib/python{sys.version_info.major}.{sys.version_info.minor}/PyQt6/Qt6/qml",
]

for file in removeFiles:
    try:
        rmFile = shutil.rmtree(file)
        print(f"Removing: {file}")
    except NotADirectoryError:
        os.remove(file)
    except FileNotFoundError:
        pass
