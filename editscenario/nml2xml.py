#!/usr/bin/env python2

from __future__ import print_function

import sys, os, os.path

# If we are running from bbpy source: add xmlstore, xmlplot, gotmgui directories to the search path.
rootdir = os.path.dirname(os.path.realpath(__file__))
if os.path.isdir(os.path.join(rootdir, '../../xmlstore/xmlstore')):
    print('Detected that we are running from BBpy source. Using local xmlstore/xmlplot/gotmgui.')
    sys.path.insert(0, os.path.join(rootdir, '../../xmlstore'))
    sys.path.insert(0, os.path.join(rootdir, '../../xmlplot'))
    sys.path.insert(0, os.path.join(rootdir, '../../gotmgui'))

import gotmgui.core.common, gotmgui.core.scenario, xmlstore.xmlstore

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Converts a directory with namelist files (NMLPATH) into an XML-based values file (XMLPATH), using an XML-based schema that describes the namelist structure. The path to the schema (SCHEMAPATH) may point to a single schema file, or to a directory with schemas (and other metadata such as converters, default values). In the latter case, the program will try to auto-detect the newest applicable schema, and then convert the values to the desired version (see --targetversion option) if that is specified.')
    parser.add_argument('schemapath',help='File/folder with schema(s) and optionally converters')
    parser.add_argument('nmlpath',help='Directory with namelist file(s)')

    parser.add_argument('--targetversion',help='Desired version to be used for the exported values file. If needed, values will be converted from the namelist version to this desired version. Note that this argument is only used if the provided SCHEMAPATH is a directory.')
    parser.add_argument('--root',help='Schema node to be used as root. By specifying this, a subset of the schema can be converted (e.g., a single namelist file).')
    parser.add_argument('-q','--quiet', action='store_true', help='Suppress output of progress messages')
    parser.add_argument('-e','--export', nargs=2, help='Output type: xml = XML-based values file, dir = directory with XML-based values file and associated data, zip = zip file with XML-based values file and associated data.')
    parser.set_defaults(quiet=False,targetversion=None,root=None,export='xml')
    options = parser.parse_args()

    schemapath = options.schemapath
    nmlpath    = options.nmlpath

    # Check if the source path exists.
    if not os.path.exists(schemapath):
        print('Error! The schema path "%s" does not exist.' % schemapath)
        return 1
    if not os.path.exists(nmlpath):
        print('Source path "%s" does not exist.' % nmlpath)
        return 1

    if not options.quiet:
        gotmgui.core.common.verbose = True

    # Add custom GOTM data types if possible.
    try:
        import xmlstore.datatypes,xmlplot.data
        xmlstore.datatypes.register('gotmdatafile',xmlplot.data.LinkedFileVariableStore)
    except ImportError:
        pass

    if os.path.isfile(schemapath):
        # A single schema file is specified.
        if options.targetversion is not None:
            print('--targetversion argument is only used if the schema path is a directory. When it is a file, the exported values will always have the version of the specified schema.')
            return 2
        scen = gotmgui.core.scenario.NamelistStore(schemapath)
        scen.loadFromNamelists(nmlpath,strict=False,root=options.root)
    else:
        # A directory with one or more schema files (and potentially converters) is specified.
        class Scenario(gotmgui.core.scenario.NamelistStore):
            @classmethod
            def getSchemaInfo(cls):
                return xmlstore.xmlstore.schemainfocache[schemapath]
        try:
            scen = Scenario.fromNamelists(nmlpath,targetversion=options.targetversion,root=options.root)
        except Exception as e:
            raise
            print('Could not find a schema that matches the namelists. Details:\n%s' % e)
            return 1

    # Export to scenario.
    exportformat = None
    targetpath = None
    if options.export:
        exportformat = options.export[0]
        targetpath = options.export[1]
        if not options.quiet:
            print('Saving values to "%s"...' % targetpath)
        if exportformat=='xml':
            scen.save(targetpath)
        else:
            scen.saveAll(targetpath,targetisdir=exportformat=='dir')
    else:
        print('No exports done - use -e otion')

    # Clean-up (delete temporary directories etc.)
    scen.release()

    return 0

# If the script has been run (as opposed to imported), enter the main loop.
if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
