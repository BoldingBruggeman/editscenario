#!/usr/bin/env python

import sys, os, os.path, optparse

# Get GOTM-GUI directory from environment.
if 'GOTMGUIDIR' in os.environ:
    relguipath = os.environ['GOTMGUIDIR']
elif 'GOTMDIR' in os.environ:
    relguipath = os.path.join(os.environ['GOTMDIR'],'gui.py')
else:
    print 'Cannot find GOTM-GUI directory. Please set environment variable "GOTMDIR" to the GOTM root (containing gui.py), or "GOTMGUIDIR" to the GOTM-GUI root, before running.'
    sys.exit(1)

# Add the GOTM-GUI directory to the search path.
gotmguiroot = os.path.join(os.path.dirname(os.path.realpath(__file__)),relguipath)
sys.path.append(gotmguiroot)

# Import modules form GOTM-GUI.
import xmlstore.xmlstore,core.scenario

# Generic scenario class which takes all schema and converter information from a directory [schemapath].
schemapath = None
class Scenario(core.scenario.NamelistStore):
    @classmethod
    def getSchemaInfo(cls):
        return xmlstore.xmlstore.schemainfocache[schemapath]

def main():
    defschemadir = os.path.abspath(os.path.join(os.path.dirname(__file__),'schema'))

    import optparse
    parser = optparse.OptionParser(usage = 'usage: %prog [options] VALUESFILE [OUTPUTPATH] [assignments]')
    parser.add_option('--schemadir',type='string',help='Directory where metadata (schemas, converters, default values) reside. Defaults to "%s".' % defschemadir)
    parser.add_option('-g','--gui',action='store_true',help='Show the GUI for scenario editing.')
    parser.add_option('-q','--quiet',action='store_false',dest='verbose',help='Suppress progress messages.')
    parser.add_option('--skipvalidation',action='store_false',dest='validate',help='Skip scenario validation')
    parser.add_option('-e','--export',choices=('nml','xml','dir','zip'),help='Save the modified scenario in the specified format: "xml" for a new XML-based values file, "dir" for a directory containing the XML-based values file plus associated data, "zip" for a ZIP file containing the XML-based values file plus associated data, and "nml" for a directory with namelist files. If this option is set, the OUTPUTPATH argument specifying the output path (directory or file, depending on the chosen export format) must be provided.')
    parser.add_option('--targetversion',type='string',help='Desired values version to operate upon during GUI editing, validation, and export. If needed, values will be converted from their source version to this desired version upon load.')
    parser.add_option('--root',type='string',help='Schema node to be used as root. If this is set, the corresponding subset of the schema will be shown on screen (with -g/--gui), validated, and exported to the namelist format (with -e/--export nml). It can be used to export a single namelist file only.')
    parser.set_defaults(export=None,gui=False,verbose=True,validate=True,schemadir=defschemadir,root=None,targetversion=None)
    (options, args) = parser.parse_args()
    
    global schemapath
    schemapath = options.schemadir

    if options.export:
        if len(args)<2:
            print 'Two arguments required: the path to the values file and the output path.'
            return 2
    elif len(args)<1:
        print 'One argument required: the path to the values file.'
        return 2
    
    # Get unnamed command line arguments
    valuespath = os.path.abspath(args.pop(0))
    if options.export:
        targetpath = os.path.abspath(args.pop(0))

    # Add custom GOTM data types if possible.
    try:
        import xmlstore.datatypes,xmlplot.data
        xmlstore.datatypes.register('gotmdatafile',xmlplot.data.LinkedFileVariableStore)

        if options.gui: import xmlplot.gui_qt4
    except ImportError:
        pass

    # Open the scenario
    targetstore = None
    if options.targetversion is not None: targetstore = Scenario.fromSchemaName(options.targetversion)
    try:
        # First try to open the target path as a data container.
        scen = Scenario.fromContainer(valuespath,targetstore=targetstore)
    except:
        # Check if the source path exist.
        if not os.path.isfile(valuespath):
            print 'Error! The XML values file "%s" does not exist.' % valuespath
            return 1
        scen = Scenario.fromXmlFile(valuespath,targetstore=targetstore)
    if options.verbose: print 'Operating on values file with version %s.' % scen.version
    
    context = {'container':xmlstore.datatypes.DataContainerDirectory(os.getcwd())}
    def processAssignments(assignments,ignoremissing=False,quiet=False):
        for name,val in assignments:
            node = scen.findNode(name)
            if node is None:
                if ignoremissing: continue
                if options.verbose: print 'Node "%s" was not found in scenario.' % name
                return False
                
            fullname = '/'.join(node.location)
            if len(val)>1 and val[0] in '\'"' and val[0]==val[-1]: val = val[1:-1]
            tp = node.getValueType(returnclass=True)
            try:
                val = tp.fromXmlString(val,context,node.templatenode)
                if not quiet: print '"%s": assigning value "%s".' % (fullname,val.toPrettyString())
                node.setValue(val)
                if isinstance(val,xmlstore.util.referencedobject): val.release()
            except Exception,e:
                print '"%s": cannot assign value "%s". %s' % (fullname,val,e)
        return True

    # Process environment-based assignments
    processAssignments(os.environ.items(),ignoremissing=True,quiet=not options.verbose)
    
    # Process command line assignments
    assignments = []
    for assignment in args:
        if '=' not in assignment:
            print 'Error: "%s" is not a valid assignment. Assignments must follow the pattern VARIABLE=VALUE.' % assignment
            return 2
        assignments.append(assignment.split('=',1))
    if not processAssignments(assignments,quiet=not options.verbose): return 2

    # If a root node was specified, locate it within the schema.
    rootnode = None
    if options.root is not None:
        rootnode = scen[options.root]
        if rootnode is None:
            print 'Node "%s" was not found in schema.' % options.root
            sys.exit(2)
        node2role = scen.detectNodeRolesInNamelist()
        if options.gui and len(rootnode.children)==0:
            print 'Node "%s" contains no child nodes. Such nodes cannot be used as root if -g/--gui is specified.' % '/'.join(rootnode.location)
            sys.exit(2)
        if options.export=='nml':
            if node2role[rootnode]==2:
                print 'Node "%s" represents a namelist, rather than a directory or file. Such nodes cannot be used as root if --export nml is specified.' % '/'.join(rootnode.location)
                sys.exit(2)
            elif node2role[rootnode]==3:
                print 'Node "%s" represents a namelist variable, rather than a directory or file. Such nodes cannot be used as root if --export nml is specified.' % '/'.join(rootnode.location)
                sys.exit(2)

    if options.gui:
        # Show scenario editor
        from PyQt4 import QtGui
        import xmlstore.gui_qt4
        app = QtGui.QApplication([' '])
        dialog = xmlstore.gui_qt4.PropertyEditorDialog(None,scen,title='Scenario editor',loadsave=True,rootnode=rootnode)
        dialog.resize(500,600)
        dialog.show()
        dialog.resizeColumns()
        app.exec_()

    if options.validate: 
        # Validate the scenario
        nodes = None
        if rootnode is not None: nodes = rootnode.getDescendants()
        errors = scen.validate(nodes)
        if errors:
            print 'Validation failed! Errors:'
            for error in errors: print error
            if options.export:
                print 'Nothing done because scenario validation failed (specify --skipvalidation if you want to ignore validation errors).'
                return 1
        elif options.verbose:
            if options.root is not None:
                print 'Scenario subset %s validated successfully.' % '/'.join(rootnode.location)
            else:
                print 'Scenario validated successfully.'

    # Export the scenario
    if options.export=='nml':
        if options.verbose: print 'Exporting values to namelist file(s) %s...' % targetpath
        scen.writeAsNamelists(targetpath,addcomments=True,allowmissingvalues=True,root=options.root)
    elif options.export=='xml':
        if options.verbose: print 'Exporting values to XML-based values file (%s)...' % targetpath
        scen.save(targetpath)
    elif options.export=='dir':
        if options.verbose: print 'Exporting packaged values to directory (%s)...' % targetpath
        scen.saveAll(targetpath,targetisdir=True)
    elif options.export=='zip':
        if options.verbose: print 'Exporting packaged values to ZIP file (%s)...' % targetpath
        scen.saveAll(targetpath)
    else:
        if options.verbose: print 'No further action taken.'

    # Clean-up (delete temporary directories etc.)
    scen.release()
    
    return 0

# If the script has been run (as opposed to imported), enter the main loop.
if (__name__=='__main__'):
    ret = main()
    sys.exit(ret)
