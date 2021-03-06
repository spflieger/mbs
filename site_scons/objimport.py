# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------- #
#   Copyright (C) 2010 by Christoph Thelen                                #
#   doc_bacardi@users.sourceforge.net                                     #
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
#   This program is distributed in the hope that it will be useful,       #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#   GNU General Public License for more details.                          #
#                                                                         #
#   You should have received a copy of the GNU General Public License     #
#   along with this program; if not, write to the                         #
#   Free Software Foundation, Inc.,                                       #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
# ----------------------------------------------------------------------- #


import os
import subprocess

import SCons.Script


def objimport_action(target, source, env):
    # Get the section name.
    strSectionName = env['OBJIMPORT_SECTIONNAME']

    # Get the old path. This must be restored at the end of the function.
    strOldPath = os.getcwd()

    # Get the source path and file.
    (strSrcPath, strSrcFile) = os.path.split(source[0].get_path())
    # Get the target path.
    strDstPath = os.path.abspath(target[0].get_path())

    # Get the binary architecture.
    strAsicTyp = env['ASIC_TYP']
    strOutputArchitecture = 'Unknown'
    strBinaryArchitecture = 'Unknown'
    if strAsicTyp == 'NETIOL':
        strOutputArchitecture = 'elf32-littleriscv'
        strBinaryArchitecture = 'RISCV'
    else:
        strOutputArchitecture = 'elf32-littlearm'
        strBinaryArchitecture = 'ARM'

    # Change to the folder of the sourcefile.
    os.chdir(os.path.abspath(strSrcPath))
    iReturnCode = subprocess.call([
        env['OBJCOPY'],
        '-v',
        '-I',
        'binary',
        '-O', strOutputArchitecture,
        '-B', strBinaryArchitecture,
        '--rename-section', '.data=%s' % strSectionName,
        strSrcFile,
        strDstPath
    ])

    # Move back to the old folder.
    os.chdir(strOldPath)

    if iReturnCode != 0:
        raise Exception('Failed to convert the source to an object file!')


def objimport_emitter(target, source, env):
    # Make the target depend on the parameter.
    env.Depends(target, SCons.Node.Python.Value(env['OBJIMPORT_SECTIONNAME']))

    return target, source


def objimport_string(target, source, env):
    return 'ObjImport %s' % target[0].get_path()


def ApplyToEnv(env):
    # ------------------------------------------------------------------------
    #
    # Add ObjImport builder.
    #
    env['OBJIMPORT_SECTIONNAME'] = '.rodata'

    objimport_act = SCons.Action.Action(objimport_action, objimport_string)
    objimport_bld = SCons.Script.Builder(
        action=objimport_act,
        emitter=objimport_emitter,
        suffix='$OBJSUFFIX',
        single_source=1
    )
    env['BUILDERS']['ObjImport'] = objimport_bld
