"""
    Author: Ural Security System Centre (based on Felipe Molina de la Torre)
    Date: November 2019
    Summary: Import a tree from Metasploit database
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

import gettext
import mimetypes
import os
import sys
from xml.dom import minidom

_ = gettext.gettext

import pygtk
pygtk.require('2.0')
from gtk import gdk
import gtk.glade
import gobject

import keepnote
from keepnote import unicode_gtk
from keepnote.notebook import NoteBookError, get_valid_unique_filename,\
    CONTENT_TYPE_DIR, attach_file
from keepnote import notebook as notebooklib
from keepnote import tasklib, safefile
from keepnote.gui import extension, FileChooserDialog
from netaddr import IPAddress, IPNetwork

try:
    import pygtk
    pygtk.require('2.0')
    from gtk import gdk
    import gtk.glade
    import gobject
except ImportError:
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
            window, "Import Metasploit workspace", _("Import Metasploit workspace"),
            lambda w: self.on_import_nmap(
                window, window.get_notebook()),
            tooltip=_("Import a tree of folder extracted from a Metasploit workspace"))
        
        # TODO: Fix up the ordering on the affected menus.
        self.add_ui(window,
            """
            <ui>
            <menubar name="main_menu_bar">
               <menu action="File">
                 <menu action="Import">
                     <menuitem action="Import Metasploit workspace"/>
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
            "Import Metasploit workspace", window, 
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
                window.set_status("Metasploit workspace files imported.")
            return True
    
        except NoteBookError:
            if window:
                window.set_status("")
                window.error("Error while importing Metasploit workspace files.", 
                             e, sys.exc_info()[2])
            else:
                self.app.error("Error while importing Metasploit workspace files.", 
                               e, sys.exc_info()[2])
            return False

        except Exception, e:
            if window:
                window.set_status("")
                window.error("unknown error", e, sys.exc_info()[2])
            else:
                self.app.error("unknown error", e, sys.exc_info()[2])
            return False

class Host:
    def __init__(self, ip):
        self._id = int( IPAddress(ip) )
        self.ip = ip
        self.services = []

class Service:
    def __init__(self, port):
        self._id = int(port)
        self.port = port

def get_net_icon(cidr):
    mypath = os.path.dirname(os.path.abspath(__file__))
    return "%s/icons/network.png" % mypath

def get_software_icon(banner):
    banner = banner.lower()
    mypath = os.path.dirname(os.path.abspath(__file__))
    if (banner.find("apache") >= 0):
        return "%s/icons/software/apache.png" % mypath
    elif (banner.find("iis") >= 0):
        return "%s/icons/software/iis.png" % mypath
    elif (banner.find("nginx") >= 0):
        return "%s/icons/software/nginx.png" % mypath
    elif (banner.find("tomcat") >= 0):
        return "%s/icons/software/tomcat.png" % mypath

def get_os_icon(hos):
    hlos = hos.lower()
    mypath = os.path.dirname(os.path.abspath(__file__))
    
    if (hlos.find("windows") >= 0 and hlos.find("2000") >= 0):
        return "%s/icons/os/win2000.png" % mypath
    if (hlos.find("windows") >= 0 and (hlos.find("xp") >= 0 or hlos.find("2003") >= 0)):
        return "%s/icons/os/winxp.png" % mypath
    elif (hlos.find("windows") >= 0 and hlos.find("vista") >= 0):
        return "%s/icons/os/vista.png" % mypath
    elif (hlos.find("windows") >= 0 and (hlos.find("7") >= 0 or hlos.find("2008") >= 0)):
        return "%s/icons/os/win7.png" % mypath
    elif (hlos.find("windows") >= 0 and (hlos.find("8") >= 0 or hlos.find("2012") >= 0)):
        return "%s/icons/os/win8.png" % mypath
    elif (hlos.find("windows") >= 0 and (hlos.find("10") >= 0 or hlos.find("2016") >= 0)):
        return "%s/icons/os/win10.png" % mypath
    elif (hlos.find("windows") >= 0):
        return "%s/icons/os/win7.png" % mypath
    
    elif (hlos.find("centos") >= 0):
        return "%s/icons/os/centos.png" % mypath
    elif (hlos.find("fedora") >= 0):
        return "%s/icons/os/fedora.png" % mypath
    elif (hlos.find("ubuntu") >= 0):
        return "%s/icons/os/ubuntu.png" % mypath
    elif (hlos.find("debian") >= 0):
        return "%s/icons/os/debian.png" % mypath
    elif (hlos.find("linux") >= 0):
        return "%s/icons/os/linux.png" % mypath

    elif (hlos.find("freebsd") >= 0):
        return "%s/icons/os/freebsd.png" % mypath

    elif (hlos.find("solaris") >= 0):
        return "%s/icons/os/solaris.png" % mypath

    elif (hlos.find("mac") >= 0 and hlos.find("os") >= 0):
        return "%s/icons/os/osx.png" % mypath

    elif (hlos.find("cisco") >= 0):
        return "%s/icons/hw/cisco.png" % mypath
    elif (hlos.find("dlink") >= 0 or hlos.find("mikrotik") >= 0):
        return "%s/icons/hw/router.png" % mypath

    elif (hlos.find("checkpoint") >= 0):
        return "%s/icons/hw/checkpoint.png" % mypath
    elif (hlos.find("juniper") >= 0):
        return "%s/icons/hw/juniper.png" % mypath
    elif (hlos.find("f5") >= 0):
        return "%s/icons/hw/f5.png" % mypath    
    elif (hlos.find("HP-UX") >= 0):
        return "%s/icons/hw/hp.png" % mypath
    elif (hlos.find("vmware") >= 0):
        return "%s/icons/hw/vmware.png" % mypath
    else:
        return None   

def get_subnet(where, ip):
    ipaddr = IPAddress(ip)
    for node in where.get_children():
        try:
            if ipaddr in IPNetwork( node.get_basename().split()[0].replace('-','/') ):
                return node
        except:
            pass

def get_hostnode(where, ip):
    for node in where.get_children():
        if node.get_basename().split()[0] == ip:
            return node

def get_servicenode(where, port):
    for node in where.get_children():
        if node.get_basename().split('-')[0] == port:
            return node


def import_nmap(node, filename, index=None, task=None):
    """
    Import a MSF XML single file into the notebook

    node     -- node to attach folder to
    filename -- filename of text file to import
    task     -- Task object to track progress
    """

    if task is None:
        task = tasklib.Task()

    msfxml = minidom.parse(filename)

    hosts = []
    for hostnode in msfxml.getElementsByTagName("host"):
        if not hostnode.getElementsByTagName("address"):
            continue
        host = Host(ip=hostnode.getElementsByTagName("address")[0].childNodes[0].nodeValue)
        print "[*] parsed host %s" % host.ip
        host.mac = hostnode.getElementsByTagName("mac")[0].childNodes[0].nodeValue if hostnode.getElementsByTagName("mac")[0].childNodes else ''
        host.hostname = hostnode.getElementsByTagName("name")[0].childNodes[0].nodeValue if hostnode.getElementsByTagName("name")[0].childNodes else ''
        host.os = hostnode.getElementsByTagName("os-name")[0].childNodes[0].nodeValue if hostnode.getElementsByTagName("os-name")[0].childNodes else ''
        host.info = hostnode.getElementsByTagName("info")[0].childNodes[0].nodeValue if hostnode.getElementsByTagName("info")[0].childNodes else ''
        host.comments = hostnode.getElementsByTagName("comments")[0].childNodes[0].nodeValue if hostnode.getElementsByTagName("comments")[0].childNodes else ''
        host.vulns = int(hostnode.getElementsByTagName("vuln-count")[0].childNodes[0].nodeValue) if hostnode.getElementsByTagName("vuln-count")[0].childNodes else 0
        for servicenode in hostnode.getElementsByTagName("services")[0].getElementsByTagName("service"):
            service = Service(port=servicenode.getElementsByTagName("port")[0].childNodes[0].nodeValue)
            service.proto = servicenode.getElementsByTagName("proto")[0].childNodes[0].nodeValue
            service.state = servicenode.getElementsByTagName("state")[0].childNodes[0].nodeValue if servicenode.getElementsByTagName("state")[0].childNodes else ''
            service.name = servicenode.getElementsByTagName("name")[0].childNodes[0].nodeValue if servicenode.getElementsByTagName("name")[0].childNodes else ''
            service.info = servicenode.getElementsByTagName("info")[0].childNodes[0].nodeValue if servicenode.getElementsByTagName("info")[0].childNodes else ''
            host.services.append(service)
        hosts.append(host)    

    hosts.sort(key=lambda h:h._id)
    i = 0
    for host in hosts:
        i += 1
        subnetnode = get_subnet(where=node, ip=host.ip)
        if not subnetnode:
            cidr = str(IPNetwork("%s/24"%host.ip).cidr)
            subnetnode = node.new_child(notebooklib.CONTENT_TYPE_PAGE, cidr)
            subnetnode.set_attr("title", cidr)
            with safefile.open(subnetnode.get_data_file(), "w", codec="utf-8") as o:
                o.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
                o.close()
            subnetnode.set_attr("icon", get_net_icon(cidr))

        hostnode = get_hostnode(where=subnetnode, ip=host.ip)
        if not hostnode:
            hostnode = subnetnode.new_child(notebooklib.CONTENT_TYPE_PAGE, host.ip)
            print "[+] %d/%d added new host %s" % (i,len(hosts),host.ip)
        else:
            print "[+] %d/%d updated host %s" % (i,len(hosts),host.ip)
        
        #import pdb;pdb.set_trace()
        hostinfo = "{ip} {hostname} {mac}".format( ip=host.ip, hostname=host.hostname, mac=host.mac )
        hostnode.set_attr("title", hostinfo)
        with safefile.open(hostnode.get_data_file(), "w", codec="utf-8") as o:
            o.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
            if host.mac:
                o.write('<span>%s</span><br/>' % host.mac)
            if host.hostname:
                o.write('<span>%s</span><br/>' % host.hostname)
            o.write("</body></html>")
            o.close()

        if get_os_icon(host.os):
            hostnode.set_attr("icon", get_os_icon(host.os))

        if host.vulns > 0:
            hostnode.set_attr("title_fgcolor","#770000")
            subnetnode.set_attr("title_fgcolor","#770000")

        if host.comments.find('wned') != -1:
            hostnode.set_attr("title_fgcolor","#FFFFFF")
            hostnode.set_attr("title_bgcolor","#770000")
            subnetnode.set_attr("title_fgcolor","#FFFFFF")
            subnetnode.set_attr("title_bgcolor","#770000")

        host.services.sort(key=lambda s:s._id)
        for service in host.services:
            servicenode = get_servicenode(where=hostnode, port=service.port)
            if not servicenode:
                servicenode = hostnode.new_child(notebooklib.CONTENT_TYPE_PAGE, service.port)
            if service.info and get_software_icon(service.info):
                servicenode.set_attr("icon", get_software_icon(service.info))

            serviceinfo = "{port}/{proto} {name} {info}".format(port=service.port, proto=service.proto, name=service.name, info=service.info)
            servicenode.set_attr("title", serviceinfo)
            with safefile.open(servicenode.get_data_file(),"w",codec="utf-8") as o:
                o.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><body>""")
                o.write("<span>%s</span><br/>" % (service.info))
                o.write("</body></html>")
                o.close()

            if service.state == 'filtered':
                servicenode.set_attr("title_fgcolor","#555555")
            elif service.state == 'closed':
                servicenode.set_attr("title_fgcolor","#000000")


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

