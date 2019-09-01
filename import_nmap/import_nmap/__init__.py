"""

    Author: Felipe Molina de la Torre
    Date: November 2013
    Summary: Import a tree from nmap output XML files

"""

#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
#

# python imports
# import codecs
import gettext
import mimetypes
import os
import sys
# import re
# from xml.sax.saxutils import escape
from xml.dom import minidom

_ = gettext.gettext


# pygtk imports
import pygtk
pygtk.require('2.0')
from gtk import gdk
import gtk.glade
import gobject

# keepnote imports
import keepnote
from keepnote import unicode_gtk
from keepnote.notebook import NoteBookError, get_valid_unique_filename,\
    CONTENT_TYPE_DIR, attach_file
from keepnote import notebook as notebooklib
from keepnote import tasklib, safefile
from keepnote.gui import extension, FileChooserDialog

# pygtk imports
try:
    import pygtk
    pygtk.require('2.0')
    from gtk import gdk
    import gtk.glade
    import gobject
except ImportError:
    # do not fail on gtk import error,
    # extension should be usable for non-graphical uses
    pass



class Extension (extension.Extension):

    def __init__(self, app):
        """Initialize extension"""
        
        extension.Extension.__init__(self, app)
        self.app = app


    def get_depends(self):
        return [("keepnote", ">=", (0, 7, 1))]


    def on_add_ui(self, window):
        """Initialize extension for a particular window"""
        
        # add menu options
        self.add_action(
            window, "Import Nmap XML", _("Import Nmap XML"),
            lambda w: self.on_import_nmap(
                window, window.get_notebook()),
            tooltip=_("Import a tree of folder extracted from a nmap scan result file"))
        
        # TODO: Fix up the ordering on the affected menus.
        self.add_ui(window,
            """
            <ui>
            <menubar name="main_menu_bar">
               <menu action="File">
                 <menu action="Import">
                     <menuitem action="Import Nmap XML"/>
                 </menu>
               </menu>
            </menubar>
            </ui>
            """)

    def on_import_nmap(self, window, notebook):
        """Callback from gui for importing a plain text file"""
        
        # Ask the window for the currently selected nodes
        nodes = window.get_selected_nodes()
        if len(nodes) == 0:
            return
        node = nodes[0]

        dialog = FileChooserDialog(
            "Import Nmap XML", window, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=("Cancel", gtk.RESPONSE_CANCEL,
                     "Import", gtk.RESPONSE_OK))
        dialog.set_select_multiple(True)
        response = dialog.run()

        if response == gtk.RESPONSE_OK and dialog.get_filenames():
            filenames = map(unicode_gtk, dialog.get_filenames())
            dialog.destroy()

            self.import_nmap_xml(node, filenames, window=window)
        else:
            dialog.destroy()


    def import_nmap_xml(self, node, filenames, window=None):
        try:
            for filename in filenames:
                import_nmap(node, filename, task=None)

            if window:
                window.set_status("Nmap XML files imported.")
            return True
    
        except NoteBookError:
            if window:
                window.set_status("")
                window.error("Error while importing nmap files.", 
                             e, sys.exc_info()[2])
            else:
                self.app.error("Error while importing nmap files.", 
                               e, sys.exc_info()[2])
            return False

        except Exception, e:
            if window:
                window.set_status("")
                window.error("unknown error", e, sys.exc_info()[2])
            else:
                self.app.error("unknown error", e, sys.exc_info()[2])
            return False

def get_os_icon(hos):
    hlos = hos.lower()
    mypath = os.path.dirname(os.path.abspath(__file__))
    
    # NOTE: For now, not using re as this produces a slower import
    if (hlos.find("freebsd") >= 0): #.search('.*freebsd.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/freebsd.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("xp") >= 0): #(re.search('.*windows\s+xp.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/winxp.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("nt") >= 0): # (re.search('.*windows\s+nt.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/winxp.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("vista") >= 0): # (re.search('.*windows\s+vista.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/win7.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("7") >= 0): # (re.search('.*windows\s+7.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/win7.png" % mypath
    elif (hlos.find("mac") >= 0 and hlos.find("os") >= 0): # (re.search('.*mac\s+os.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/mac.png" % mypath
    elif (hlos.find("solaris") >= 0): # (re.search('.*solaris.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/solaris.png" % mypath
    elif (hlos.find("linux") >= 0): # (re.search('.*linux.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/linux.png" % mypath
    elif (hlos.find("qemu") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/qemu.png" % mypath
    elif (hlos.find("blue coat") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/bluecoat.png" % mypath
    elif (hlos.find("juniper") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/juniper.png" % mypath
    elif (hlos.find("f5") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/f5.png" % mypath
    elif (hlos.find("cisco") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/cisco.png" % mypath
    elif (hlos.find("windows") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/winxp.png" % mypath
    elif (hlos.find("HP-UX") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/hp.png" % mypath
    elif (hlos.find("SonicWALL") >= 0): # (re.search('.*qemu.*',hos,flags=re.IGNORECASE) is not None):
        return "%s/icons/sonicwall.png" % mypath
    else:
        return None    

def import_nmap(node, filename, index=None, task=None):
    """
    Import a nmap XML single file into the notebook

    node     -- node to attach folder to
    filename -- filename of text file to import
    task     -- Task object to track progress
    """

    if task is None:
        # create dummy task if needed
        task = tasklib.Task()

    nmapxml = minidom.parse(filename)

    for hostnode in nmapxml.getElementsByTagName("host"):
        ip = ''
        mac = ''
        dns_a = []
        dns_ptr = []

        if len(hostnode.getElementsByTagName("address")) > 0:
            ip = hostnode.getElementsByTagName("address")[0].getAttribute("addr")
            if len(hostnode.getElementsByTagName("address")) > 1:
                mac = hostnode.getElementsByTagName("address")[1].getAttribute("addr")
                mac += " " + hostnode.getElementsByTagName("address")[1].getAttribute("vendor")

        if len(hostnode.getElementsByTagName("hostnames")) > 0:
            for hostname in hostnode.getElementsByTagName("hostnames")[0].getElementsByTagName("hostname"):
                if hostname.getAttribute("type") == "user":
                    dns_a.append( hostname.getAttribute("name") )
                elif hostname.getAttribute("type") == "PTR":
                    dns_ptr.append( hostname.getAttribute("name") )


        hostinfo = "{ip} {hostnames} {mac}".format( ip=ip, hostnames=','.join(dns_a + dns_ptr), mac=mac )
        host = node.new_child(notebooklib.CONTENT_TYPE_PAGE, hostinfo)
        host.set_attr("title", hostinfo)
        with safefile.open(host.get_data_file(), "w", codec="utf-8") as o:
            o.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
            if mac:
                o.write('<span>%s</span><br/>' % mac)
            for hostname in dns_a:
                o.write('<span style="color: #00ff00">%s A</span><br/>' % hostname)
            for hostname in dns_ptr:
                o.write('<span style="color: #00ffff">%s PTR</span><br/>' % hostname)
            o.write("</body></html>")
            o.close()

        #host.set_attr("icon","note-green.png")

        if len(hostnode.getElementsByTagName("ports")) > 0:
            for portnode in hostnode.getElementsByTagName("ports")[0].getElementsByTagName("port"):
                pnumber = portnode.getAttribute("portid")
                pprotocol = portnode.getAttribute("protocol")

                if len(portnode.getElementsByTagName("state")) > 0:
                    statenode = portnode.getElementsByTagName("state")[0]
                    pstate = statenode.getAttribute("state")
                    pstatereason = statenode.getAttribute("reason")
                    pttl = statenode.getAttribute("reason_ttl")
                    
                if len(portnode.getElementsByTagName("service")) > 0:
                    servicenode = portnode.getElementsByTagName("service")[0]
                    pservicename = servicenode.getAttribute("name")
                    pserviceproduct = servicenode.getAttribute("product")
                    pserviceversion = servicenode.getAttribute("version")
                    pextrainfo = servicenode.getAttribute("extrainfo")

                serviceinfo = "{service} {ver}".format(service=pserviceproduct, ver=pserviceversion) if pserviceproduct else pservicename
                portinfo = "{port}/{proto} ttl={ttl} {service}".format(port=pnumber, proto=pprotocol, ttl=pttl, service=serviceinfo)
                port = host.new_child(notebooklib.CONTENT_TYPE_PAGE, portinfo)
                port.set_attr("title", portinfo)
                with safefile.open(port.get_data_file(),"w",codec="utf-8") as o:
                    o.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
                    o.write("Service: %s<br/>Product: %s<br/>Version: %s<br/>Info: %s<br/>" % (pservicename, pserviceproduct, pserviceversion, pextrainfo))
                    o.write("</body></html>")
                    o.close()
                if pstate == 'open':
                    port.set_attr("title_fgcolor","#00AA00")
                elif pstate == 'filtered':
                    port.set_attr("title_fgcolor","#555555")
                elif pstate == 'closed':
                    port.set_attr("title_fgcolor","#000000")

    task.finish()
                     

def escape_whitespace(line):
    """Escape white space for an HTML line"""

    line2 = []
    it = iter(line)

    # replace leading spaces
    for c in it:
        if c == " ":
            line2.append("&nbsp;")
        else:
            line2.append(c)
            break

    # replace multi-spaces
    for c in it:
        if c == " ":
            line2.append(" ")
            for c in it:
                if c == " ":
                    line2.append("&nbsp;")
                else:
                    line2.append(c)
                    break
        else:
            line2.append(c)

    return "".join(line2)
    


if __name__ == "__main__":
    print "Use this as an extension for Keepnote, this is not a command line program..."
    exit(1)
